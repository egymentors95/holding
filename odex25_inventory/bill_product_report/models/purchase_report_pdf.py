from odoo import models, fields, api
from odoo import http
from odoo.http import request
import json

class BillProductReportController(http.Controller):

    @http.route('/bill_product_report/html', type='http', auth='user')
    def open_html_report(self, **kwargs):
        context_data = kwargs.get('context')
        if context_data:
            context_data = json.loads(context_data)
        else:
            context_data = {}

        data = context_data.get('data', {})
        docids = kwargs.get('docids')
        if docids:
            docids = [int(x) for x in docids.split(',')]
        else:
            docids = []

        pdf_content, _ = request.env.ref(
            'bill_product_report.report_action_invoice_bill_html'
        )._render_qweb_html(docids, data=data)

        return request.make_response(pdf_content, [
            ('Content-Type', 'text/html'),
            ('Content-Length', len(pdf_content)),
        ])


class PurchaseBillReport(models.AbstractModel):
    _name = 'report.bill_product_report.purchase_bill_html_report'
    _description = 'Purchase Bill HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('Data received in report:', data)
        return {
            'report_data': data or {},
            'docs': self.env['purchase.bill.wizard'].browse(docids),
        }
