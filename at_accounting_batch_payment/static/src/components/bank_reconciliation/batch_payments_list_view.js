/** @odoo-module **/

import { registry } from "@web/core/registry";
import { EmbeddedListView } from "@at_accounting/components/bank_reconciliation/embedded_list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useState, onWillUnmount } from "@odoo/owl";

export class BankRecBatchPaymentsRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.globalState = useState(this.env.methods.getState());
        onWillUnmount(this.saveSearchState);
    }

    /** @override **/
    getRowClass(record) {
        const classes = super.getRowClass(record);
        const selectedBatchIds = this.globalState.bankRecRecordData.selected_batch_ids || [];
        if (selectedBatchIds.includes(record.resId)) {
            return `${classes} o_rec_widget_list_selected_item table-info`;
        }
        return classes;
    }

    /** @override **/
    async onCellClicked(record, column, ev) {
        // We only add for now. In Odoo 19, clicking again removes.
        // For simplicity, let's just trigger the add action.
        const action = this.env.methods.actionAddBatchPayment
            || this.env.config.actionAddBatchPayment;

        if (action) {
            await action(record.resId);
        } else {
            console.error(
                "[BatchPayments] actionAddBatchPayment not found in env.methods or env.config.",
                "env.methods keys:", Object.keys(this.env.methods || {}),
            );
        }
    }

    /** Backup the search facets in order to restore them when the user comes back on this view. **/
    saveSearchState() {
        const initParams = this.globalState.bankRecEmbeddedViewsData
            && this.globalState.bankRecEmbeddedViewsData.batch_payments;
        if (!initParams) return;
        const searchModel = this.env.searchModel;
        if (searchModel) {
            initParams.exportState = { searchModel: JSON.stringify(searchModel.exportState()) };
        }
    }
}

export const BankRecBatchPayments = {
    ...EmbeddedListView,
    Renderer: BankRecBatchPaymentsRenderer,
};

registry.category("views").add("bank_rec_batch_payments_list_view", BankRecBatchPayments);
