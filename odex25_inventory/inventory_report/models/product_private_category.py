from odoo import models, fields


class ProductPrivateCategory(models.Model):
    _name = 'product.private.category'
    _description = 'الفئة الخاصة للمنتج'

    name = fields.Char(string='اسم الفئة الخاصة', required=True)
