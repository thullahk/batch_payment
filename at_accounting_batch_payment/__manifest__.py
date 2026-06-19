{
    'name': 'Batch Payment for Community',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Enterprise-grade Batch Payment & Bank Reconciliation for Odoo Community Accounting.',
    'description': """
Batch Payment for Community
============================

Bring Enterprise-level Batch Payment functionality to Odoo 18 Community Edition with AT Accounting.

**Key Features:**

* **Batch Payment Management** – Create, validate, and track inbound & outbound batch payments with a full lifecycle workflow (New → Sent → Reconciled).
* **Bank Reconciliation Integration** – A dedicated "Batch Payments" tab inside the bank reconciliation widget lets you match entire batches against bank statement lines in one click.
* **Smart Unpacking** – During reconciliation validation, batch lines are automatically expanded into individual journal items for accurate accounting entries.
* **One-Click Batch Creation** – Select multiple payments from the kanban view and group them into a batch instantly.
* **Multi-Currency Support** – Handles batches with payments in different currencies, with proper conversion and residual tracking.
* **Batch Print & Export** – Print batch payment reports or generate export files for bank submission.
* **Payment Method Filtering** – Automatically filters and validates payments by method, journal, and type.
* **Error & Warning Wizard** – Built-in validation wizard catches issues (draft payments, wrong states, duplicate entries) before sending.
* **Chatter & Activity Tracking** – Full audit trail with mail thread integration on every batch record.

**Who is it for?**

Odoo Community users who need to group cheque deposits, vendor payments, or customer receipts
into single bank transactions — without upgrading to Enterprise.

**Requirements:**

* Odoo 18 Community Edition
* AT Accounting (Community Accounting module)
    """,
    'author': 'Digitz Technologies',
    'website': 'https://digitz.ae',
    'support': 'support@digitz.ae',
    'depends': ['at_accounting', 'account_batch_payment'],
    'data': [
        'views/account_batch_payment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'at_accounting_batch_payment/static/src/components/bank_reconciliation/kanban.js',
            'at_accounting_batch_payment/static/src/components/bank_reconciliation/batch_payments_list_view.js',
            'at_accounting_batch_payment/static/src/components/bank_reconciliation/bank_rec_form.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 0,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
