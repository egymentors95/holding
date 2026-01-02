from odoo import api, models


class ReportBtCash(models.AbstractModel):
    _name = 'report.account_statement_report.report_bt_cash_pdf'
    _description = 'BT Cash Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizards = self.env['bt.cash.wizard'].browse(docids)

        report_data_list = [w.get_report_data() for w in wizards]

        return {
            'doc_ids': docids,
            'doc_model': 'bt.cash.wizard',
            'docs': wizards,
            'report_data_list': report_data_list,
        }
