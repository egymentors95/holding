from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
    )