from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        default=lambda self: self.env.user.operation_type,
        states={'draft': [('readonly', False)]})
