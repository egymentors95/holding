from odoo import models, fields, api


class SalesPlanLines(models.Model):
    _name = 'sales.plan.lines'
    _description = 'Sales Plan Lines'

    sales_plan_id = fields.Many2one(comodel_name='sales.plan', string='Sales Plan')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    price_total = fields.Float(string='Total Price', compute='_compute_price_total', store=True)
    quantity_per_month = fields.Float(string='Quantity per Month', compute='_compute_quantity_per_month', store=True)
    price_total_per_month = fields.Float(string='Price Total per Month', compute='_compute_price_total', store=True)

    @api.depends('price_total', 'sales_plan_id.number_of_months')
    def _compute_price_total(self):
        for record in self:
            if record.sales_plan_id.number_of_months:
                record.price_total_per_month = record.price_total / record.sales_plan_id.number_of_months
            else:
                record.price_total_per_month = 0.0


    @api.depends('quantity', 'sales_plan_id.number_of_months')
    def _compute_quantity_per_month(self):
        for record in self:
            if record.sales_plan_id.number_of_months:
                record.quantity_per_month = record.quantity / record.sales_plan_id.number_of_months
            else:
                record.quantity_per_month = 0.0

    @api.depends('quantity', 'price')
    def _compute_price_total(self):
        for record in self:
            record.price_total = record.quantity * record.price