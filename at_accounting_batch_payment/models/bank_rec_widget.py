import logging
from odoo import _, models, fields, api, Command

_logger = logging.getLogger(__name__)


class BankRecWidgetLine(models.Model):
    _inherit = 'bank.rec.widget.line'

    batch_payment_id = fields.Many2one('account.batch.payment')
    source_aml_ids = fields.Json()

    flag = fields.Selection(selection_add=[('batch_payment', 'batch_payment')])

    @api.depends('flag', 'source_aml_ids')
    def _compute_name(self):
        super()._compute_name()
        for line in self:
            if line.flag == 'batch_payment' and line.source_aml_ids:
                aml_count = len(line.source_aml_ids)
                line.name = _("Includes %s payment(s)") % aml_count

    @api.depends('flag', 'batch_payment_id')
    def _compute_source_aml_fields(self):
        super()._compute_source_aml_fields()
        for line in self:
            if line.flag == 'batch_payment' and line.batch_payment_id:
                line.source_aml_move_name = line.batch_payment_id.name

    @api.depends('flag', 'batch_payment_id')
    def _compute_account_id(self):
        super()._compute_account_id()
        for line in self:
            if line.flag == 'batch_payment' and line.batch_payment_id:
                # Use a default account or the first payment's account
                line.account_id = line.batch_payment_id.journal_id.default_account_id


class BankRecWidget(models.Model):
    _inherit = 'bank.rec.widget'

    selected_batch_ids = fields.Json(compute='_compute_selected_batch_ids')

    @api.depends('line_ids.flag', 'line_ids.batch_payment_id')
    def _compute_selected_batch_ids(self):
        for wizard in self:
            wizard.selected_batch_ids = wizard.line_ids.filtered(lambda l: l.flag == 'batch_payment').batch_payment_id.ids

    def _prepare_embedded_views_data(self):
        res = super()._prepare_embedded_views_data()

        bank_filter = {
            'name': 'journal_id',
            'description': 'Bank',
            'domain': str([('journal_id', '=', self.st_line_id.journal_id.id)]),
            'is_default': True,
        }

        res['batch_payments'] = {
            'domain': [('state', '!=', 'reconciled')],
            'dynamic_filters': [bank_filter],
            'context': {
                'search_default_unreconciled': 1,
                'search_view_ref': 'at_accounting_batch_payment.view_batch_payment_search_bank_rec_widget',
                'list_view_ref': 'at_accounting_batch_payment.view_batch_payment_list_bank_rec_widget',
            },
        }
        return res

    def _lines_prepare_batch_payment_line(self, batch, amls):
        self.ensure_one()
        currencies = batch.payment_ids.currency_id
        currency = currencies if len(currencies) == 1 else self.env['res.currency']
        return {
            'flag': 'batch_payment',
            'batch_payment_id': batch.id,
            'source_aml_ids': amls.ids,
            'currency_id': currency.id,
            'amount_currency': -batch.amount_residual_currency,
            'balance': -batch.amount_residual,
            'source_amount_currency': -batch.amount_residual_currency,
            'source_balance': -batch.amount_residual,
            'date': batch.date,
        }

    def _js_action_add_batch_payment(self, batch_id):
        """
        Called via todo_command when a batch payment row is clicked.
        Groups all AMLs into a single 'batch_payment' line for visual grouping.
        """
        self.ensure_one()
        batch = self.env['account.batch.payment'].browse(batch_id)

        # Gather all possible AMLs to match
        amls = self.env['account.move.line']
        for payment in batch.payment_ids:
            if payment.move_id:
                liquidity_lines, _cp, _wo = payment._seek_for_lines()
                amls |= liquidity_lines.filtered(lambda l: not l.reconciled)

        linked_invoices = batch.payment_ids.invoice_ids
        if linked_invoices:
            invoice_amls = linked_invoices.line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
                and not l.reconciled
            )
            amls |= invoice_amls

        if amls:
            # Remove existing lines for this batch if any (to toggle)
            existing_line = self.line_ids.filtered(lambda l: l.flag == 'batch_payment' and l.batch_payment_id.id == batch_id)
            if existing_line:
                self.line_ids = [Command.delete(existing_line.id)]
            else:
                self.line_ids = [Command.create(self._lines_prepare_batch_payment_line(batch, amls))]

        # Recompute the balancing line so the suspense suggestion is removed
        # as soon as the batch payment fully matches the statement line.
        self._lines_add_auto_balance_line()
        self._action_clear_manual_operations_form()

        return self._js_action_mount_line_in_edit(self.line_ids.filtered(lambda x: x.flag == 'liquidity').index)

    def _action_expand_batch_payments(self, lines):
        self.ensure_one()
        batch_lines = lines.filtered(lambda l: l.flag == 'batch_payment')
        if not batch_lines:
            return
        amls = self.env['account.move.line']
        for line in batch_lines:
            amls |= self.env['account.move.line'].browse(line.source_aml_ids)
        self._action_remove_lines(batch_lines)
        self._action_add_new_amls(amls, allow_partial=False)

    def _action_validate(self):
        self.ensure_one()
        self._action_expand_batch_payments(self.line_ids)
        super()._action_validate()

    def _validation_lines_vals(self, line_ids_create_command_list, aml_to_exchange_diff_vals, to_reconcile):
        """
        Unpacks batch_payment lines into real AMLs during validation.
        """
        partners = (self.line_ids.filtered(lambda x: x.flag != 'liquidity')).partner_id
        partner_to_set = partners if len(partners) == 1 else self.env['res.partner']
        source2exchange = self.line_ids.filtered(lambda l: l.flag == 'exchange_diff').grouped('source_aml_id')
        
        for line in self.line_ids:
            if line.flag == 'exchange_diff':
                continue

            if line.flag == 'batch_payment':
                # UNPACK BATCH
                amls = self.env['account.move.line'].browse(line.source_aml_ids)
                for aml in amls:
                    to_reconcile.append((len(line_ids_create_command_list) + 1, aml))
                    line_ids_create_command_list.append(Command.create({
                        'name': aml.name or aml.move_id.name,
                        'account_id': aml.account_id.id,
                        'partner_id': aml.partner_id.id or partner_to_set.id,
                        'currency_id': aml.currency_id.id,
                        'amount_currency': -aml.amount_residual_currency,
                        'balance': -aml.amount_residual,
                        'sequence': len(line_ids_create_command_list) + 1,
                    }))
                continue

            # Standard logic for other lines
            amount_currency = line.amount_currency
            balance = line.balance
            if line.flag == 'new_aml':
                to_reconcile.append((len(line_ids_create_command_list) + 1, line.source_aml_id))
                exchange_diff = source2exchange.get(line.source_aml_id)
                if exchange_diff:
                    aml_to_exchange_diff_vals[len(line_ids_create_command_list) + 1] = {
                        'amount_residual': exchange_diff.balance,
                        'amount_residual_currency': exchange_diff.amount_currency,
                        'analytic_distribution': exchange_diff.analytic_distribution,
                    }
                    amount_currency += exchange_diff.amount_currency
                    balance += exchange_diff.balance
            
            line_ids_create_command_list.append(Command.create(line._get_aml_values(
                sequence=len(line_ids_create_command_list) + 1,
                partner_id=partner_to_set.id if line.flag in ('liquidity', 'auto_balance') else line.partner_id.id,
                amount_currency=amount_currency,
                balance=balance,
            )))
