from odoo import models, fields, api


class StockLocations(models.Model):
    _inherit = 'stock.location'


    user_id = fields.Many2one(comodel_name='res.users', string='User')
