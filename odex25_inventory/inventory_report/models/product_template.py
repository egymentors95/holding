from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dos = fields.Integer(string='جرعة')
    private_category_id = fields.Many2one(comodel_name='product.private.category', string='الفئة الخاصة')