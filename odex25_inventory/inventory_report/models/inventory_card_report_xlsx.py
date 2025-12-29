from odoo import api, models

class ReportInventoryCard(models.AbstractModel):
    _name = 'report.inventory_report.inventory_card_pdf'
    _description = 'Inventory Card PDF Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'inventory.card',
            'docs': self.env['inventory.card'].browse(docids),
            'data': data or {},
            'lines': data.get('lines', []) if data else [],
            'date_from': data.get('date_from') if data else False,
            'date_to': data.get('date_to') if data else False,
        }
