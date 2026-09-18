/** @odoo-module */

import { Component } from "@odoo/owl";

export class AccountReportEllipsisPopover extends Component {
    static template = "at_accounting.AccountReportEllipsisPopover";
    static props = {
        close: Function,
        name: String,
        copyEllipsisText: Function,
    };
}
