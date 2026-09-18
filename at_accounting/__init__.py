from . import models
from . import wizard
from . import controllers

from odoo import Command

import logging

_logger = logging.getLogger(__name__)


def _at_accounting_post_init(env):
    country_code = env.company.country_id.code
    if country_code:
        module_list = []

        sepa_zone = env.ref('base.sepa_zone', raise_if_not_found=False)
        sepa_zone_country_codes = sepa_zone and sepa_zone.mapped('country_ids.code') or []

        if country_code in sepa_zone_country_codes:
            module_list.extend(['account_iso20022', 'account_bank_statement_import_camt'])

        module_ids = env['ir.module.module'].search([('name', 'in', module_list), ('state', '=', 'uninstalled')])
        if module_ids:
            module_ids.sudo().button_install()

    for company in env['res.company'].search([('chart_template', '!=', False)], order="parent_path"):
        ChartTemplate = env['account.chart.template'].with_company(company)
        ChartTemplate._load_data({
            'res.company': ChartTemplate._get_account_accountant_res_company(company.chart_template),
        })

    country_code = env.company.country_id.code
    if country_code:
        module_list = []

        if country_code in ('AU', 'CA', 'US'):
            module_list.append('account_reports_cash_basis')

        module_ids = env['ir.module.module'].search([('name', 'in', module_list), ('state', '=', 'uninstalled')])
        if module_ids:
            module_ids.sudo().button_install()

    for company in env['res.company'].search([]):
        company.account_tax_periodicity_journal_id = company._get_default_misc_journal()
        company.account_tax_periodicity_journal_id.show_on_dashboard = True
        company._initiate_account_onboardings()


def uninstall_hook(env):
    group_basic = env.ref('account.group_account_basic')
    group_manager = env.ref('account.group_account_manager')
    if group_basic:
        group_basic.write({
            'users': [Command.clear()],
            'category_id': env.ref("base.module_category_hidden").id,
        })
        group_manager.write({
            'implied_ids': [Command.unlink(group_basic.id)],
        })


    try:
        group_user = env.ref("account.group_account_user")
        group_user.write({
            'name': "Show Full Accounting Features",
            'implied_ids': [(3, env.ref('account.group_account_invoice').id)],
            'category_id': env.ref("base.module_category_hidden").id,
        })
        group_readonly = env.ref("account.group_account_readonly")
        group_readonly.write({
            'name': "Show Full Accounting Features - Readonly",
            'category_id': env.ref("base.module_category_hidden").id,
        })
    except ValueError as e:
        _logger.warning(e)

    try:
        group_manager = env.ref("account.group_account_manager")
        group_manager.write({'name': "Billing Manager",
                             'implied_ids': [(4, env.ref("account.group_account_invoice").id),
                                             (3, env.ref("account.group_account_readonly").id),
                                             (3, env.ref("account.group_account_user").id)]})
    except ValueError as e:
        _logger.warning(e)

    # make the account_accountant features disappear (magic)
    env.ref("account.group_account_user").write({'users': [(5, False, False)]})
    env.ref("account.group_account_readonly").write({'users': [(5, False, False)]})


    invoicing_menu = env.ref("account.menu_finance")
    menus_to_move = [
        "account.menu_finance_receivables",
        "account.menu_finance_payables",
        "account.menu_finance_entries",
        "account.menu_finance_reports",
        "account.menu_finance_configuration",
        "account.menu_board_journal_1",
    ]
    for menu_xmlids in menus_to_move:
        try:
            env.ref(menu_xmlids).parent_id = invoicing_menu
        except ValueError as e:
            _logger.warning(e)
