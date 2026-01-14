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
    po_entry_count = fields.Integer(
        string='Journal Entries',
        compute='_compute_journal_entry_count'
    )
    state = fields.Selection(
        selection_add=[('stock_keeper', 'Stock Keeper')],
    )
    driver_id = fields.Many2one(comodel_name='res.users', string='Driver')
    driver_model_id = fields.Many2one(comodel_name='driver.driver', string='Driver Model')
    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    state2 = fields.Selection([
        ('draft', 'Draft'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ], default='draft', string='Driver Status')
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

    def button_stock_keeper(self):
        for rec in self:
            rec.state = 'stock_keeper'

    def button_send_to_driver(self):
        driver = self.env['driver.driver']

        for picking in self:
            if not picking.driver_id:
                raise UserError(_("Please assign a driver first."))

            driver_lines_vals = []
            for move in picking.move_line_ids_without_package:
                driver_lines_vals.append((0, 0, {
                    'product_id': move.product_id.id,
                    'quantity': move.qty_done,
                    'price': move.price_unit,
                    'location_id': move.location_id.id,
                    'uom_id': move.product_uom_id.id,
                }))

            driver_record = driver.create({
                'date': fields.Datetime.now(),
                'driver_id': picking.driver_id.id,
                'stock_id': picking.id,
                'source': picking.name,
                'sale_id': picking.sale_id.id if picking.sale_id else False,
                'driver_line_ids': driver_lines_vals,
            })

            self.env['mail.activity'].create({
                'res_id': driver_record.id,
                'res_model_id': self.env['ir.model']._get('driver.driver').id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'user_id': picking.driver_id.id,
                'summary': _('New Delivery Assigned'),
                'note': _('You have a new delivery to handle.'),
                'date_deadline': fields.Date.today(),
            })
            self.driver_model_id = driver_record.id
            self.state2 = 'out_for_delivery'

            picking.message_post(body=_("Driver record %s created and activity sent to driver.") % driver_record.name)

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
                    # if not rec.attachment_ids:
                    #     raise UserError(_("Attachments is Mandatory"))
                    if rec.types_out == 'driver' and not rec.driver_id:
                        raise UserError(_("Driver is Mandatory"))

        # res = super(StockPicking, self).button_validate()
        # for picking in self:
        #     sale_order = picking.sale_id
        #     if not sale_order or sale_order.state != 'sale':
        #         continue
        #
        #     product_lot_qty = {}
        #
        #     for ml in picking.move_line_ids:
        #         if not ml.lot_id or ml.qty_done <= 0:
        #             continue
        #
        #         key = (ml.product_id.id, ml.lot_id.id)
        #         product_lot_qty.setdefault(key, 0)
        #         product_lot_qty[key] += ml.qty_done
        #
        #     for product_id in set(k[0] for k in product_lot_qty.keys()):
        #         lot_items = [
        #             (lot_id, qty)
        #             for (pid, lot_id), qty in product_lot_qty.items()
        #             if pid == product_id
        #         ]
        #
        #         so_lines = sale_order.order_line.filtered(
        #             lambda l: l.product_id.id == product_id and not l.display_type
        #         )
        #         if not so_lines:
        #             continue
        #
        #         base_line = so_lines[0]
        #
        #         # أول Lot → update
        #         first_lot_id, first_qty = lot_items[0]
        #         base_line.write({
        #             'lot_id': first_lot_id,
        #             'product_uom_qty': first_qty,
        #
        #         })
        #
        #         # باقي الـ Lots → create new lines
        #         for lot_id, qty in lot_items[1:]:
        #             base_line.copy({
        #                 'order_id': sale_order.id,
        #                 'product_id': base_line.product_id.id,
        #                 'price_unit': base_line.price_unit,
        #                 'tax_id': [(6, 0, base_line.tax_id.ids)],
        #                 'lot_id': lot_id,
        #                 'product_uom_qty': qty,
        #
        #             })

            # بعد ما اللاينات اتحدثت
        return super(StockPicking, self).button_validate()
