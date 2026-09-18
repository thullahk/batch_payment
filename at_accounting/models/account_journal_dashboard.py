from odoo import models
import ast

class account_journal(models.Model):
    _inherit = "account.journal"

    def action_open_reconcile(self):
        self.ensure_one()

        if self.type in ('bank', 'cash', 'credit'):
            return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
                default_context={
                    'default_journal_id': self.id,
                    'search_default_journal_id': self.id,
                    'search_default_not_matched': True,
                },
            )
        else:
            # Open reconciliation view for customers/suppliers
            return self.env['ir.actions.act_window']._for_xml_id('at_accounting.action_move_line_posted_unreconciled')

    def action_open_to_check(self):
        self.ensure_one()
        return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
            default_context={
                'search_default_to_check': True,
                'search_default_journal_id': self.id,
                'default_journal_id': self.id,
            },
        )

    def action_open_bank_transactions(self):
        self.ensure_one()
        return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
            default_context={
                'search_default_journal_id': self.id,
                'default_journal_id': self.id
             },
            kanban_first=False,
        )

    def action_open_reconcile_statement(self):
        return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
            default_context={
                'search_default_statement_id': self.env.context.get('statement_id'),
            },
        )

    def open_action(self):
        # EXTENDS account
        # set default action for liquidity journals in dashboard

        if self.type in ('bank', 'cash', 'credit') and not self._context.get('action_name'):
            self.ensure_one()
            return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
                extra_domain=[('line_ids.account_id', '=', self.default_account_id.id)],
                default_context={
                    'default_journal_id': self.id,
                    'search_default_journal_id': self.id,
                },
            )
        return super().open_action()

    def _fill_general_dashboard_data(self, dashboard_data):
        super()._fill_general_dashboard_data(dashboard_data)
        for journal in self.filtered(lambda journal: journal.type == 'general'):
            dashboard_data[journal.id]['is_account_tax_periodicity_journal'] = journal == journal.company_id._get_tax_closing_journal()

    def action_open_bank_balance_in_gl(self):
        ''' Show the bank balance inside the General Ledger report.
        :return: An action opening the General Ledger.
        '''
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("at_accounting.action_account_report_general_ledger")

        action['context'] = dict(ast.literal_eval(action['context']), default_filter_accounts=self.default_account_id.code)

        return action
