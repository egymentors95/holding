from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.constrains('product_id.lst_price', 'price_unit')
    def _check_price_unit(self):
        for line in self:
            if line.price_unit < line.product_id.lst_price:
                raise models.ValidationError(
                    "The unit price cannot be lower than the product's list price."
                )