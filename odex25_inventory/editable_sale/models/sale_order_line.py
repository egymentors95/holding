from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
        domain="[('product_id', '=', product_id)]"
    )

    @api.onchange('product_id', 'order_id.warehouse_id')
    def _onchange_product_id_set_lot_by_warehouse(self):
        if not self.product_id or not self.order_id.warehouse_id:
            self.lot_id = False
            return

        warehouse = self.order_id.warehouse_id
        location = warehouse.lot_stock_id  # Internal Location بتاعة الـ Warehouse

        # البحث عن Quant فيه كمية
        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', 'child_of', location.id),
            ('quantity', '>', 0),
            ('lot_id', '!=', False),
        ], limit=1)

        self.lot_id = quant.lot_id if quant else False

    @api.constrains('product_id.lst_price', 'price_unit')
    def _check_price_unit(self):
        for line in self:
            if self.env.user.has_group('editable_sale.group_editable_sale_order'):
                continue
            if line.price_unit < line.product_id.lst_price:
                raise models.ValidationError(
                    "The unit price cannot be lower than the product's list price."
                )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)

        if self.lot_id:
            res['lot_id'] = self.lot_id.id

        return res