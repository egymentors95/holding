from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    allowed_user_ids = fields.Many2many(
        'res.users',
        string='Allowed Users',
        help='Users allowed to see/use this category',
        relation='product_category_allowed_user_rel',
        column1='category_id',
        column2='user_id',
    )
