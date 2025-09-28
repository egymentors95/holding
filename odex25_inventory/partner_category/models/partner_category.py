from odoo import models, fields, api


class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    name = fields.Char(string='Name')


