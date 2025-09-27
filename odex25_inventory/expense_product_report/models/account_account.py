from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_partner = fields.Boolean()
    is_analytic = fields.Boolean()