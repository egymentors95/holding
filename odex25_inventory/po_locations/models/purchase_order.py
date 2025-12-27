from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()

        for order in self:
            pickings = self.env['stock.picking'].search([
                ('origin', '=', order.name),
                ('purchase_order_id', '=', False),
            ])
            pickings.write({
                'purchase_order_id': order.id
            })

        return res

    def action_create_invoice(self):
        res = super().action_create_invoice()

        if isinstance(res, dict) and res.get('res_id'):
            move = self.env['account.move'].browse(res['res_id'])
            if move and len(self) == 1:
                move.purchase_order = self.id

        return res

