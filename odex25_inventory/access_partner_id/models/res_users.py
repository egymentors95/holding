from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account')
    is_driver = fields.Boolean()