# Batch Payment for Community

**Enterprise-grade Batch Payment & Bank Reconciliation for Odoo 18 Community Edition**

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-purple.svg)](https://www.odoo.com)

---

## Overview

This module brings the powerful **Batch Payment** functionality — traditionally available only in Odoo Enterprise — to the Community Edition. It integrates seamlessly with **AT Accounting** to provide full batch payment management and bank reconciliation capabilities.

## Features

### 🗂️ Batch Payment Management
- Create **Inbound** (customer receipts) and **Outbound** (vendor payments) batches
- Auto-generated sequence references (BATCH/IN/2024/0001)
- Full lifecycle workflow: **New → Sent → Reconciled**
- Payment method filtering and validation
- Built-in error & warning wizard

### 🏦 Bank Reconciliation Integration
- Dedicated **"Batch Payments" tab** in the bank reconciliation widget
- **Click-to-match** — select a batch to reconcile all its payments at once
- **Smart unpacking** — batch lines expand into individual journal items during validation
- **Quick navigation** — click batch name to view the full record

### 📊 List & Kanban Views
- Color-coded status badges (New, Sent, Reconciled)
- Separate menus for Customer & Vendor batch payments
- Activity tracking and scheduling
- Print & export batch reports

### ⚙️ Technical Highlights
- Multi-currency support with proper conversion
- Duplicate payment detection across batches
- Auto-posting of draft payments during validation
- SEPA file generation hooks
- Full chatter & mail thread integration

## Dependencies

| Module | Description |
|--------|-------------|
| `at_accounting` | AT Accounting (Community Accounting) |
| `account_batch_payment` | Base Batch Payment module |

## Installation

1. Copy the `at_accounting_batch_payment` folder to your Odoo addons path
2. Restart the Odoo server
3. Update the module list: **Settings → Apps → Update Apps List**
4. Install the module (it auto-installs when both dependencies are present)

## Usage

1. **Register Payments** — Record individual customer/vendor payments as usual
2. **Create Batch** — Go to Accounting → Customers/Vendors → Batch Payments → Create
3. **Add Payments** — Select payments to include in the batch
4. **Validate** — Click "Validate" to mark payments as sent
5. **Reconcile** — In bank reconciliation, use the "Batch Payments" tab to match

## Author

**Digitz Technologies**
- 📧 Email: support@digitz.ae
- 🌐 Website: [digitz.ae](https://digitz.ae)

## License

This module is licensed under the [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0) license.
