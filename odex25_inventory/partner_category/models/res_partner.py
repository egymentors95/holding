from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_category = fields.Many2one(comodel_name='partner.category', string='Partner Category')

