from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    product_category = fields.Integer(string='Product Category ID')

    @api.constrains('product_category')
    def _check_unique_product_category(self):
        for rec in self:
            if rec.product_category and rec.product_category > 0:
                existing = self.search([
                    ('product_category', '=', rec.product_category),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing:
                    raise ValidationError("Product Category ID must be unique!")
