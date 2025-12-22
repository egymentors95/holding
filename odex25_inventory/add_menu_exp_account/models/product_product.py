from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    categ_name = fields.Char(compute='_get_categ_name', store=True)

    @api.depends('categ_id.name', 'categ_id')
    def _get_categ_name(self):
        for rec in self:
            if not rec.categ_name and rec.categ_id:
                rec.categ_name = rec.categ_id.name

