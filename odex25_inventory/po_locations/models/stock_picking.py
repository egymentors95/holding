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

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        picking_type_id = res.get('picking_type_id')
        if picking_type_id:
            picking_type = self.env['stock.picking.type'].browse(picking_type_id)
            if picking_type.code == 'internal':
                # لو internal خلي الدومين Internal فقط
                res['location_id'] = False
                res['location_dest_id'] = False

        return res

    @api.onchange('picking_type_code')
    def _onchange_picking_type_location_dest(self):
        if self.picking_type_code == 'internal':
            return {
                'domain': {
                    'location_dest_id': [('usage', '=', 'internal')]
                }
            }
        else:
            return {
                'domain': {
                    'location_dest_id': [
                        ('usage', 'in', [
                            'supplier',
                            'internal',
                            'customer',
                            'inventory',
                            'production',
                            'transit'
                        ])
                    ]
                }
            }

    @api.onchange('picking_type_code')
    def _onchange_picking_type_location(self):
        if self.picking_type_code == 'internal':
            return {
                'domain': {
                    'location_id': [('usage', '=', 'internal')]
                }
            }
        else:
            return {
                'domain': {
                    'location_id': [
                        ('usage', 'in', [
                            'supplier',
                            'internal',
                            'customer',
                            'inventory',
                            'production',
                            'transit'
                        ])
                    ]
                }
            }

    def _compute_journal_entry_count(self):
        for picking in self:
            # جميع القيود المرتبطة بالحركات المخزنية للـ Picking
            moves = self.env['account.move'].search([
                ('stock_move_id', 'in', picking.move_lines.ids),
                ('purchase_order', '!=', False),
                ('move_type', '=', 'entry'),
            ])
            picking.po_entry_count = len(moves)

    def action_assign(self):
        for rec in self:
            if rec.picking_type_code == 'internal':
                if rec.location_id:
                    if not rec.location_id.user_id:
                        raise UserError('Please Add User in Source Location')
                    if rec.location_id.user_id != self.env.user:
                        raise UserError(_(
                            "You are not allowed to Check Availability this picking.\n"
                            "Only %s can Check Availability it."
                        ) % rec.location_id.user_id.name)
        return super(StockPicking, self).action_assign()



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
            if rec.picking_type_code == 'internal':
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

