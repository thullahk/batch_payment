
/** @odoo-module */

import { AccountReport } from "@at_accounting/components/account_report/account_report";
import { AccountReportLineCell } from "@at_accounting/components/account_report/line_cell/line_cell";
const { DateTime } = luxon;


export class PartnerLedgerLineCell extends AccountReportLineCell {
    static template = "at_accounting.PartnerLedgerLineCell";
    get cellClasses() {
        let superCellClasses = super.cellClasses;
        const cell = this.props.cell;
        if (
            cell.figure_type === 'date'
            && cell.expression_label == 'date_maturity'
            && cell.no_format
            && DateTime.fromISO(cell.no_format) < DateTime.now()
        ) {
            superCellClasses += ' text-danger';
        }
        return superCellClasses;
    }
}

AccountReport.registerCustomComponent(PartnerLedgerLineCell);
