from collections import defaultdict
from odoo import Command, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def set_batch_payment_bank_statement_line(self, batch_payment_id):
        """Mount a batch payment's AMLs onto the current statement line for reconciliation."""
        self.ensure_one()
        batch = self.env['account.batch.payment'].browse(batch_payment_id)

        # Post any draft payments in the batch first
        draft_payments = batch.payment_ids.filtered(lambda p: p.state == 'draft')
        if draft_payments:
            draft_payments.action_post()

        # Build the AML values to attach to the statement line's move
        amls_to_create = []
        payment2amls = defaultdict(self.env['account.move.line'].browse)

        # Get the journal's outstanding payment accounts to match against
        journal = self.journal_id
        valid_accounts = (
            journal._get_journal_inbound_outstanding_payment_accounts()
            | journal._get_journal_outbound_outstanding_payment_accounts()
        ) - journal.default_account_id

        payments_with_move = batch.payment_ids.filtered(lambda p: p.move_id)
        for payment in payments_with_move:
            liquidity_lines, _counterpart, _writeoff = payment._seek_for_lines()
            # Filter to lines on the outstanding payment accounts
            matching_lines = liquidity_lines.filtered(lambda l: l.account_id in valid_accounts)
            if not matching_lines:
                # Fall back to all liquidity lines if no match
                matching_lines = liquidity_lines
            payment2amls[payment] = matching_lines

        for payment, move_lines in payment2amls.items():
            for move_line in move_lines:
                amls_to_create.append(
                    move_line._get_aml_values(
                        balance=-move_line.balance,
                        amount_currency=-move_line.amount_currency,
                        reconciled_lines_ids=[Command.set(move_line.ids)],
                        payment_lines_ids=[Command.set(payment.ids)],
                    )
                )

        if amls_to_create:
            self._add_move_line_to_statement_line_move(amls_to_create)

    def delete_reconciled_line(self, move_line_ids):
        """Deletes the specified move lines from the bank statement line after unreconciling them."""
        self.ensure_one()
        move_lines_to_remove = self.env['account.move.line'].browse(move_line_ids)
        payments = move_lines_to_remove.payment_lines_ids
        super().delete_reconciled_line(move_line_ids)
        if payments:
            # Put the payments back to in_process state
            payments.action_draft()
            payments.action_post()
            # When an invoice is linked to the payment, the move must be put back to draft
            if move_linked := payments.invoice_ids:
                move_linked.button_draft()
                move_linked.action_post()
