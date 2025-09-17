from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class SalesReportHtml(models.AbstractModel):
    _name = 'report.product_report.profitability_report_html'
    _description = 'Sales HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        # تحويل من string إلى date object
        if date_from and isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to and isinstance(date_to, str):
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

        date_from_last_year = date_from - relativedelta(years=1) if date_from else False
        date_to_last_year = date_to - relativedelta(years=1) if date_to else False

        return {
            'date_from_last_year': date_from_last_year,
            'date_to_last_year': date_to_last_year,
            'report_data': data or {},
            'docs': self.env['profitability.wizard'].browse(docids),
        }
