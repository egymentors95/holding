from odoo import models, fields, api


class InventoryReportHtml(models.AbstractModel):
    _name = 'report.inventory_report.inventory_report_html'
    _description = 'Inventory HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('Data received in report:', data)
        return {
            'report_data': data or {},
            'docs': self.env['inventory.report.wizard'].browse(docids),
        }
