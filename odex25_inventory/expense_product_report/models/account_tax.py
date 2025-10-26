from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_flag = fields.Char(string='Tax Flag', help='Custom flag for tax identification in reports.')
