from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state2 = fields.Selection([
        ('draft', 'Draft'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ], default='draft', string='Driver Status')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            stock_picking = self.env['stock.picking'].search([('origin', '=', order.name)], limit=1)
            if stock_picking:
                stock_picking.sale_id = order.id
                for move in stock_picking.move_line_ids_without_package:
                    line = order.order_line.filtered(lambda l: l.product_id == move.product_id)
                    if line:
                        move.price_unit = line.price_unit
        return res
