from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    price_unit = fields.Float(string='Unit Price')