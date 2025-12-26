from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_validate(self):
        res = super().button_validate()

        for order in self:
            # pickings اللي اتعملت من أمر الشراء
            pickings = order.picking_ids.filtered(
                lambda p: p.state not in ('cancel')
            )

            pickings.write({
                'purchase_order_id': order.id
            })

        return res
