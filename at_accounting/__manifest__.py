{
    'name': "AT Odoo 18 Community Accounting",
    'version': "18.0.1.5",
    'category': 'Accounting/Accounting',
    'sequence': 1,
    'summary': "A complete accounting toolkit for Odoo 18 Community with advanced reports, wizards, and workflows.",
    'description': """
========================================================
Your Complete Professional Accounting Suite for Odoo 18
========================================================

Transform your Odoo 18 Community into a powerful, professional-grade financial management system. This module provides the advanced tools and deep financial insights that growing businesses need to thrive. 

Move beyond standard accounting with a comprehensive toolkit designed to improve accuracy, streamline workflows, and empower you to make smarter, data-driven decisions.

Key Features:
-------------
* **Advanced Reporting Engine:** Generate a full suite of essential financial reports on-demand, including:
    * Profit and Loss (P&L)
    * Balance Sheet
    * Cash Flow Statement
    * Aged Receivables & Payables
    * General Ledger & Partner Ledger
    * Trial Balance
    * Comprehensive Tax Reports
    * ...and many more.

* **Interactive Financial Dashboards:** Visualize your financial health with intuitive and dynamic dashboard components, bringing your numbers to life.

* **Streamlined Bank Reconciliation:** Utilize an enhanced bank reconciliation widget and powerful auto-reconciliation wizards to manage your statements faster and more accurately.

* **Powerful Accounting Wizards:** Simplify complex processes with guided, user-friendly wizards for tasks like Fiscal Year Closing, Multicurrency Revaluation, and Report Exporting.

* **Guided User Tours:** Onboard your team quickly and ensure they can leverage all the powerful new features with integrated user tours.

* **Professional PDF Exports:** Create clean, professionally formatted PDF documents for all your financial reports, ready for sharing with stakeholders.

Empower Your Finance Team
-------------------------
This module provides your team with the information they need, right where they need it. Reduce manual work, eliminate errors, and give your accountants the tools they need to perform at their best.
    """,
    'icon': '/at_accounting/static/description/icon.png',
    'author': 'Rahmathullah',
    'website': '',
    'support': 'lapxortia@gmail.com',
    'depends': ['account','web_tour', 'stock_account', 'base_import'],
    'data': [
        'data/ir_cron.xml',
        'data/digest_data.xml',
        'data/at_accounting_tour.xml',
        'data/at_accounting_data.xml',
        'data/pdf_export_templates.xml',
        'data/balance_sheet.xml',
        'data/cash_flow_report.xml',
        'data/executive_summary.xml',
        'data/profit_and_loss.xml',
        'data/bank_reconciliation_report.xml',
        'data/aged_partner_balance.xml',
        'data/general_ledger.xml',
        'data/trial_balance.xml',
        'data/sales_report.xml',
        'data/partner_ledger.xml',
        'data/multicurrency_revaluation_report.xml',
        'data/deferred_reports.xml',
        'data/journal_report.xml',
        'data/generic_tax_report.xml',
        'views/account_report_view.xml',
        'data/account_report_actions.xml',
        'data/report_send_cron.xml',
        'data/menuitems.xml',
        'data/mail_activity_type_data.xml',
        'data/mail_templates.xml',

        'security/ir.model.access.csv',
        'security/at_accounting_security.xml',
        'security/accounting_security.xml',

        'views/account_account_views.xml',
        'views/account_fiscal_year_view.xml',
        'views/account_journal_dashboard_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/account_reconcile_views.xml',
        'views/account_reconcile_model_views.xml',
        'views/at_accounting_menuitems.xml',
        'views/digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/bank_rec_widget_views.xml',
        'views/report_invoice.xml',
        'views/partner_views.xml',
        'views/account_activity.xml',
        'views/account_tax_views.xml',
        'views/mail_activity_views.xml',
        'views/report_template.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',

        'wizard/account_change_lock_date.xml',
        'wizard/account_auto_reconcile_wizard.xml',
        'wizard/account_reconcile_wizard.xml',
        'wizard/reconcile_model_wizard.xml',
        'wizard/account_report_send.xml',
        'wizard/multicurrency_revaluation.xml',
        'wizard/report_export_wizard.xml',
        'wizard/account_report_file_download_error_wizard.xml',
        'wizard/fiscal_year.xml',
        'wizard/mail_activity_schedule_views.xml',
        'security/at_account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_modify_views.xml',
        # 'views/account_account_views.xml',
        'views/account_asset_views.xml',
        'views/account_asset_group_views.xml',
        # 'views/account_move_views.xml',
        'data/assets_reports.xml',
        'data/account_report_actions_depr.xml',
        'views/account_bank_statement_import_view.xml',

    ],
    'demo': [
        'demo/at_accounting_demo.xml',
        'demo/partner_bank.xml',

    ],
    'installable': True,
    'application': True,
    'post_init_hook': '_at_accounting_post_init',
    'uninstall_hook': "uninstall_hook",
    'license': 'OPL-1',
    'assets':{
        'web.assets_backend': [
            'at_accounting/static/src/js/tours/at_accounting.js',
            'at_accounting/static/src/components/**/*',
            'at_accounting/static/src/**/*.xml',
            'at_accounting/static/src/js/**/*',
            'at_accounting/static/src/widgets/**/*',
            'at_accounting/static/src/**/*',

        ],
        'web.assets_unit_tests': [
            'at_accounting/static/tests/**/*',
            ('remove', 'at_accounting/static/tests/tours/**/*'),
            'at_accounting/static/tests/*.js',
            'at_accounting/static/tests/account_report/**/*.js',
        ],
        'web.assets_tests': [
            'at_accounting/static/tests/tours/**/*',
        ],
        'at_accounting.assets_pdf_export': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            ('include', 'web._assets_bootstrap_backend'),
            'web/static/fonts/fonts.scss',
            'at_accounting/static/src/scss/**/*',
        ],
        'web.report_assets_common': [
            'at_accounting/static/src/scss/account_pdf_export_template.scss',
        ],
        'web.assets_web_dark': [
            'at_accounting/static/src/scss/*.dark.scss',
        ],
        'web.qunit_suite_tests': [
            'at_accounting/static/tests/legacy/*.js',
        ],
    },
    'price': 20,
    'currency': "EUR",
	'images': ['static/description/banner.png'],
}