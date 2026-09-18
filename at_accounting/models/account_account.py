import ast
from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    def action_open_reconcile(self):
        self.ensure_one()
        # Open reconciliation view for this account
        action_values = self.env['ir.actions.act_window']._for_xml_id('at_accounting.action_move_line_posted_unreconciled')
        domain = ast.literal_eval(action_values['domain'])
        domain.append(('account_id', '=', self.id))
        action_values['domain'] = domain
        return action_values

    exclude_provision_currency_ids = fields.Many2many('res.currency', relation='account_account_exclude_res_currency_provision', help="Whether or not we have to make provisions for the selected foreign currencies.")
    budget_item_ids = fields.One2many(comodel_name='account.report.budget.item', inverse_name='account_id')  # To use it in the domain when adding accounts from the report

    asset_model_ids = fields.Many2many(
        'account.asset',
        domain=[('state', '=', 'model')],
        help="An asset wil be created for each asset model when this account is used on a vendor bill or a refund",
        tracking=True,
    )
    create_asset = fields.Selection([('no', 'No'), ('draft', 'Create in draft'), ('validate', 'Create and validate')],
                                    required=True, default='no', tracking=True)
    # specify if the account can generate asset depending on it's type. It is used in the account form view
    can_create_asset = fields.Boolean(compute="_compute_can_create_asset")
    form_view_ref = fields.Char(compute='_compute_can_create_asset')
    # decimal quantities are not supported, quantities are rounded to the lower int
    multiple_assets_per_line = fields.Boolean(string='Multiple Assets per Line', default=False, tracking=True,
                                              help="Multiple asset items will be generated depending on the bill line quantity instead of 1 global asset.")

    @api.depends('account_type')
    def _compute_can_create_asset(self):
        for record in self:
            record.can_create_asset = record.account_type in ('asset_fixed', 'asset_non_current')
            record.form_view_ref = 'at_accountingview_account_asset_form'

    @api.onchange('create_asset')
    def _onchange_multiple_assets_per_line(self):
        for record in self:
            if record.create_asset == 'no':
                record.multiple_assets_per_line = False
