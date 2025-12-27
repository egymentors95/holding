from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

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
