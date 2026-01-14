from odoo import models, fields,api

class StockMove(models.Model):
    _inherit = 'stock.move'

    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users',
        help='Users allowed to validate this picking.',
        compute='_compute_user_ids',
        store=True,
    )

    @api.depends('location_id', 'location_dest_id')
    def _compute_user_ids(self):
        for picking in self:
            users = set()
            if picking.location_id and picking.location_id.user_id:
                users.add(picking.location_id.user_id.id)
            if picking.location_dest_id and picking.location_dest_id.user_id:
                users.add(picking.location_dest_id.user_id.id)
            picking.user_ids = [(6, 0, list(users))]

    def _create_account_move_line(
            self, credit_account_id, debit_account_id,
            journal_id, qty, description, svl_id, cost
    ):
        # نشغّل السلوك الأصلي
        res = super()._create_account_move_line(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost
        )

        # ✅ نمسك Journal Entry اللي اتعمل
        account_moves = self.env['account.move'].search([
            ('stock_move_id', '=', self.id),
            ('purchase_order', '=', False),
        ])

        # ✅ نرمي purchase_order من picking
        if self.picking_id and self.picking_id.purchase_order_id:
            account_moves.write({
                'purchase_order': self.picking_id.purchase_order_id.id
            })

        return res

        return res
