from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_category = fields.Integer(string='Product Category ID')



    @api.constrains('product_category', 'categ_id')
    def _check_unique_product_category_per_categ(self):
        for rec in self:
            if not rec.product_category or not rec.categ_id:
                continue  # لو واحد منهم فاضي، متعملش تشيك

            # دور على منتجات تانية بنفس الكاتيجوري + نفس product_category
            duplicate = self.search([
                ('id', '!=', rec.id),
                ('categ_id', '=', rec.categ_id.id),
                ('product_category', '=', rec.product_category),
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    f"Product Category number {rec.product_category} "
                    f"already exists in category {rec.categ_id.display_name}."
                )
