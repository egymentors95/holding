from odoo import models, fields, api


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
