from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Order')
    types_out = fields.Selection([
        ('driver', 'سواق'),
        ('customer', 'العميل'),
        ('charge', 'الشحن'),
    ])
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments', )
    driver_id = fields.Many2one(comodel_name='driver.driver', string='Driver')


    po_entry_count = fields.Integer(
        string='Journal Entries',
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
            if rec.picking_type_code in ['incoming', 'internal']:
                if rec.location_dest_id:
                    if not rec.location_dest_id.user_id:
                        raise UserError('Please Add User in Destination Location')
                    if rec.location_dest_id.user_id != self.env.user:
                        raise UserError(_(
                            "You are not allowed to validate this picking.\n"
                            "Only %s can validate it."
                        ) % rec.location_dest_id.user_id.name)

            if rec.picking_type_code == 'outgoing':
                if rec.types_out:
                    if not rec.attachment_ids:
                        raise UserError(_("Attachments is Mandatory"))
                    if rec.types_out == 'driver' and not rec.driver_id:
                        raise UserError(_("Driver is Mandatory"))


        return super(StockPicking, self).button_validate()

