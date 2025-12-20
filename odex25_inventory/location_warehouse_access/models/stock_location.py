from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many(comodel_name='res.users', relation='locations_users_relation', column1='location_id',
                                column2='res_id', string='Users')
