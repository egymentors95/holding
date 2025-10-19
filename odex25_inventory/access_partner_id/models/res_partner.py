from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_registration = fields.Char(string='CR')