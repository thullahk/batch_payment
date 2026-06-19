/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { BankRecKanbanController } from "@at_accounting/components/bank_reconciliation/kanban";

patch(BankRecKanbanController.prototype, {
    getChildSubEnv() {
        const subEnv = super.getChildSubEnv();
        subEnv.methods.actionAddBatchPayment = this.actionAddBatchPayment.bind(this);
        return subEnv;
    },

    notebookBatchPaymentsListViewProps() {
        const initParams = this.state.bankRecEmbeddedViewsData.batch_payments;
        return {
            type: "list",
            noBreadcrumbs: true,
            resModel: "account.batch.payment",
            searchMenuTypes: ["filter", "favorite"],
            domain: initParams.domain,
            dynamicFilters: initParams.dynamic_filters,
            context: initParams.context,
            allowSelectors: false,
            searchViewId: false,
            globalState: initParams.exportState,
            loadIrFilters: true,
        };
    },

    // Mirror of actionAddNewAml - uses the same onchange mechanism
    async actionAddBatchPayment(batchId) {
        await this.execProtectedBankRecAction(async () => {
            await this.withNewState(async (newState) => {
                await this.onchange(newState, "add_batch_payment", [batchId]);
            });
        });
    },

    async actionRedirectToBatchPayment(line) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.batch.payment",
            res_id: line.data.batch_payment_id[0],
            views: [[false, "form"]],
            target: "current",
        });
    },
});
