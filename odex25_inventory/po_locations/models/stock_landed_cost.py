from odoo import models, fields, api

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        compute='_compute_purchase_order',
        store=True
    )

    @api.depends('picking_ids.purchase_order_id', 'picking_ids')
    def _compute_purchase_order(self):
        for cost in self:
            # أول PO موجود في الحركات
            po = False
            for picking in cost.picking_ids:
                if picking.purchase_order_id:
                    po = picking.purchase_order_id
                    break
            cost.purchase_order_id = po

    def button_validate(self):
        res = super(StockLandedCost, self).button_validate()
        for rec in self:
            if rec.purchase_order_id:
                rec.account_move_id.purchase_order = rec.purchase_order_id.id
        return res

