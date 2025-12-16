from odoo import api, models


class ReportAccountStatement(models.AbstractModel):
    _name = 'report.account_statement_report.account_statement_template'
    _description = 'Customer Account Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizards = self.env['account.statement.wizard'].browse(docids)
        report_data_list = [w.get_report_data() for w in wizards]

        return {
            'doc_ids': docids,
            'doc_model': 'account.statement.wizard',
            'docs': wizards,
            'report_data_list': report_data_list,
        }




