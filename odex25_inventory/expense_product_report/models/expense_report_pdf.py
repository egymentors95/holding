from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ExpenseReportHtml(models.AbstractModel):
    _name = 'report.expense_product_report.expense_report_html'
    _description = 'Expense HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'report_data': data or {},
            'docs': self.env['profitability.wizard'].browse(docids),
        }
