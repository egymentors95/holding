from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'


    purchase_order = fields.Many2one(comodel_name='purchase.order', string='P.O')
    description_note = fields.Char(string='Purchase Order')
    description_a = fields.Char(string='Description')