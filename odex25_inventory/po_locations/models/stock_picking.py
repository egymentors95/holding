from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Order')
    po_entry_count = fields.Integer(
        string='PO Entries',
        compute='_compute_journal_entry_count'
    )

    def _compute_journal_entry_count(self):
        for picking in self:
            # جميع القيود المرتبطة بالحركات المخزنية للـ Picking
            moves = self.env['account.move'].search([
                ('stock_move_id', 'in', picking.move_lines.ids),
                ('purchase_order', '!=', False),
                ('move_type', '=', 'entry'),
            ])
            picking.po_entry_count = len(moves)

    def action_view_journal_entries(self):
        self.ensure_one()

        # القيود المرتبطة بالحركات المخزنية
        moves = self.env['account.move'].search([
            ('stock_move_id', 'in', self.move_lines.ids),
            ('purchase_order', '!=', False),
            ('move_type', '=', 'entry'),
        ])

        return {
            'name': 'Journal Entries',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', moves.ids)],
            'context': {'create': False},
        }


    def button_validate(self):
        for rec in self:
            if rec.location_dest_id:
                if not rec.location_dest_id.user_id:
                    raise UserError('Please Add User in Destination Location')
                if rec.location_dest_id.user_id != self.env.user:
                    raise UserError(_(
                        "You are not allowed to validate this picking.\n"
                        "Only %s can validate it."
                    ) % rec.location_dest_id.user_id.name)

        return super(StockPicking, self).button_validate()

