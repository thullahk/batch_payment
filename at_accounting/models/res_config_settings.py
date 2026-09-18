from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo.tools import date_utils

ACCOUNT_DOMAIN = [('deprecated', '=', False), ('account_type', 'not in',
                                               ('asset_receivable', 'liability_payable', 'asset_cash',
                                                'liability_credit_card', 'off_balance'))]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscalyear_last_day = fields.Integer(related='company_id.fiscalyear_last_day', required=True, readonly=False)
    fiscalyear_last_month = fields.Selection(related='company_id.fiscalyear_last_month', required=True, readonly=False)
    use_anglo_saxon = fields.Boolean(string='Anglo-Saxon Accounting', related='company_id.anglo_saxon_accounting', readonly=False)
    invoicing_switch_threshold = fields.Date(string="Invoicing Switch Threshold", related='company_id.invoicing_switch_threshold', readonly=False)
    group_fiscal_year = fields.Boolean(string='Fiscal Years', implied_group='at_accounting.group_fiscal_year')
    predict_bill_product = fields.Boolean(string="Predict Bill Product", related='company_id.predict_bill_product', readonly=False)

    sign_invoice = fields.Boolean(string='Authorized Signatory on invoice', related='company_id.sign_invoice', readonly=False)
    signing_user = fields.Many2one(
        comodel_name='res.users',
        string="Signature used to sign all the invoice",
        readonly=False,
        related='company_id.signing_user',
        help="Select a user here to override every signature on invoice by this user's signature"
    )
    module_sign = fields.Boolean(string='Sign', compute='_compute_module_sign_status')

    # Deferred expense management
    deferred_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        help='Journal used for deferred entries',
        readonly=False,
        related='company_id.deferred_expense_journal_id',
    )
    deferred_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        help='Account used for deferred expenses',
        readonly=False,
        related='company_id.deferred_expense_account_id',
    )
    generate_deferred_expense_entries_method = fields.Selection(
        related='company_id.generate_deferred_expense_entries_method',
        readonly=False, required=True,
        help='Method used to generate deferred entries',
    )
    deferred_expense_amount_computation_method = fields.Selection(
        related='company_id.deferred_expense_amount_computation_method',
        readonly=False, required=True,
        help='Method used to compute the amount of deferred entries',
    )

    # Deferred revenue management
    deferred_revenue_journal_id = fields.Many2one(
        comodel_name='account.journal',
        help='Journal used for deferred entries',
        readonly=False,
        related='company_id.deferred_revenue_journal_id',
    )
    deferred_revenue_account_id = fields.Many2one(
        comodel_name='account.account',
        help='Account used for deferred revenues',
        readonly=False,
        related='company_id.deferred_revenue_account_id',
    )
    generate_deferred_revenue_entries_method = fields.Selection(
        related='company_id.generate_deferred_revenue_entries_method',
        readonly=False, required=True,
        help='Method used to generate deferred entries',
    )
    deferred_revenue_amount_computation_method = fields.Selection(
        related='company_id.deferred_revenue_amount_computation_method',
        readonly=False, required=True,
        help='Method used to compute the amount of deferred entries',
    )
    totals_below_sections = fields.Boolean(related='company_id.totals_below_sections',
                                           string='Add totals below sections', readonly=False,
                                           help='When ticked, totals and subtotals appear below the sections of the report.')
    account_tax_periodicity = fields.Selection(related='company_id.account_tax_periodicity', string='Periodicity',
                                               readonly=False, required=True)
    account_tax_periodicity_reminder_day = fields.Integer(related='company_id.account_tax_periodicity_reminder_day',
                                                          string='Reminder', readonly=False, required=True)
    account_tax_periodicity_journal_id = fields.Many2one(related='company_id.account_tax_periodicity_journal_id',
                                                         string='Journal', readonly=False)

    account_reports_show_per_company_setting = fields.Boolean(
        compute="_compute_account_reports_show_per_company_setting")

    @api.depends('sign_invoice')
    def _compute_module_sign_status(self):
        sign_installed = 'sign' in self.env['ir.module.module']._installed()
        for settings in self:
            settings.module_sign = sign_installed or settings.company_id.sign_invoice

    @api.constrains('fiscalyear_last_day', 'fiscalyear_last_month')
    def _check_fiscalyear(self):
        # We try if the date exists in 2020, which is a leap year.
        # We do not define the constrain on res.company, since the recomputation of the related
        # fields is done one field at a time.
        for wiz in self:
            try:
                date(2020, int(wiz.fiscalyear_last_month), wiz.fiscalyear_last_day)
            except ValueError:
                raise ValidationError(
                    _('Incorrect fiscal year date: day is out of range for month. Month: %(month)s; Day: %(day)s',
                    month=wiz.fiscalyear_last_month, day=wiz.fiscalyear_last_day),
                )

    @api.model_create_multi
    def create(self, vals_list):
        # Amazing workaround: non-stored related fields on company are a BAD idea since the 2 fields
        # must follow the constraint '_check_fiscalyear_last_day'. The thing is, in case of related
        # fields, the inverse write is done one value at a time, and thus the constraint is verified
        # one value at a time... so it is likely to fail.
        for vals in vals_list:
            fiscalyear_last_day = vals.pop('fiscalyear_last_day', False) or self.env.company.fiscalyear_last_day
            fiscalyear_last_month = vals.pop('fiscalyear_last_month', False) or self.env.company.fiscalyear_last_month
            vals = {}
            if fiscalyear_last_day != self.env.company.fiscalyear_last_day:
                vals['fiscalyear_last_day'] = fiscalyear_last_day
            if fiscalyear_last_month != self.env.company.fiscalyear_last_month:
                vals['fiscalyear_last_month'] = fiscalyear_last_month
            if vals:
                self.env.company.write(vals)
        return super().create(vals_list)

    def open_tax_group_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tax groups',
            'res_model': 'account.tax.group',
            'view_mode': 'list',
            'context': {
                'default_country_id': self.account_fiscal_country_id.id,
                'search_default_country_id': self.account_fiscal_country_id.id,
            },
        }

    @api.depends('company_id')
    def _compute_account_reports_show_per_company_setting(self):
        custom_start_country_codes = self._get_country_codes_with_another_tax_closing_start_date()
        countries = self.env['account.fiscal.position'].search([
            ('company_id', '=', self.env.company.id),
            ('foreign_vat', '!=', False),
        ]).mapped('country_id') + self.env.company.account_fiscal_country_id
        for config_settings in self:
            config_settings.account_reports_show_per_company_setting = bool(set(countries.mapped('code')) & custom_start_country_codes)

    def open_company_dependent_report_settings(self):
        self.ensure_one()
        generic_tax_report = self.env.ref('account.generic_tax_report')
        available_reports = generic_tax_report._get_variants(generic_tax_report.id)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Configure your start dates'),
            'res_model': 'account.report',
            'domain': [('id', 'in', available_reports.ids)],
            'views': [(self.env.ref('at_accounting.account_report_tree_configure_start_dates').id, 'list')]
        }

    def _get_country_codes_with_another_tax_closing_start_date(self):
        """
        To be overridden by specific countries that wants this

        Used to know which countries can have specific start dates settings on reports

        :returns set(str):   A set of country codes from which the start date settings should be shown
        """
        return set()


    property_stock_journal = fields.Many2one(
        'account.journal', "Stock Journal",
        check_company=True,
        compute='_compute_property_stock_account',
        inverse='_set_property_stock_journal')
    property_account_income_categ_id = fields.Many2one(
        'account.account', "Income Account",
        check_company=True,
        domain=ACCOUNT_DOMAIN,
        compute='_compute_property_stock_account',
        inverse='_set_property_account_income_categ_id')
    property_account_expense_categ_id = fields.Many2one(
        'account.account', "Expense Account",
        check_company=True,
        domain=ACCOUNT_DOMAIN,
        compute='_compute_property_stock_account',
        inverse='_set_property_account_expense_categ_id')
    property_stock_valuation_account_id = fields.Many2one(
        'account.account', "Stock Valuation Account",
        check_company=True,
        domain="[('deprecated', '=', False)]",
        compute='_compute_property_stock_account',
        inverse='_set_property_stock_valuation_account_id')
    property_stock_account_input_categ_id = fields.Many2one(
        'account.account', "Stock Input Account",
        check_company=True,
        domain="[('deprecated', '=', False)]",
        compute='_compute_property_stock_account',
        inverse='_set_property_stock_account_input_categ_id')
    property_stock_account_output_categ_id = fields.Many2one(
        'account.account', "Stock Output Account",
        check_company=True,
        domain="[('deprecated', '=', False)]",
        compute='_compute_property_stock_account',
        inverse='_set_property_stock_account_output_categ_id')

    @api.depends('company_id')
    def _compute_property_stock_account(self):
        account_stock_properties_names = self._get_account_stock_properties_names()
        ProductCategory = self.env['product.category']
        for record in self:
            record = record.with_company(record.company_id)
            for fname in account_stock_properties_names:
                field = ProductCategory._fields[fname]
                record[fname] = field.get_company_dependent_fallback(ProductCategory)

    def _set_property_stock_journal(self):
        for record in self:
            record._set_property('property_stock_journal')

    def _set_property_account_income_categ_id(self):
        for record in self:
            record._set_property('property_account_income_categ_id')

    def _set_property_account_expense_categ_id(self):
        for record in self:
            record._set_property('property_account_expense_categ_id')

    def _set_property_stock_valuation_account_id(self):
        for record in self:
            record._set_property('property_stock_valuation_account_id')

    def _set_property_stock_account_input_categ_id(self):
        for record in self:
            record._set_property('property_stock_account_input_categ_id')

    def _set_property_stock_account_output_categ_id(self):
        for record in self:
            record._set_property('property_stock_account_output_categ_id')

    def _set_property(self, field_name):
        self.env['ir.default'].set('product.category', field_name, self[field_name].id, company_id=self.company_id.id)

    @api.model
    def _get_account_stock_properties_names(self):
        return [
            'property_stock_journal',
            'property_account_income_categ_id',
            'property_account_expense_categ_id',
            'property_stock_valuation_account_id',
            'property_stock_account_input_categ_id',
            'property_stock_account_output_categ_id',
        ]

