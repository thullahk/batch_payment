import { AccountReport } from "@at_accounting/components/account_report/account_report";
import { AccountReportFilters } from "@at_accounting/components/account_report/filters/filters";

export class MulticurrencyRevaluationReportFilters extends AccountReportFilters {
    static template = "at_accounting.MulticurrencyRevaluationReportFilters";

    //------------------------------------------------------------------------------------------------------------------
    // Custom filters
    //------------------------------------------------------------------------------------------------------------------
    async filterExchangeRate(ev, currencyId) {
        this.controller.options.currency_rates[currencyId].rate = ev.currentTarget.value;
    }
}

AccountReport.registerCustomComponent(MulticurrencyRevaluationReportFilters);
