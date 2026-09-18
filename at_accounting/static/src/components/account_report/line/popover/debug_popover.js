/** @odoo-module */

import { Component } from "@odoo/owl";

export class AccountReportDebugPopover extends Component {
    static template = "at_accounting.AccountReportDebugPopover";
    static props = {
        close: Function,
        expressionsDetail: Array,
        onClose: Function,
    };
}
