from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_expense = fields.Boolean()

