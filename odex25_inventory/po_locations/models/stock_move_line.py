from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    price_unit = fields.Float(string='Unit Price')

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