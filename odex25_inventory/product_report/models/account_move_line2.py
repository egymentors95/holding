from odoo import fields, models


class AccountMoveLine2(models.Model):
    _name = 'account.move.line2'
    _description = 'Temporary Profitability Report Data'

    product_category = fields.Char(string="Product Category")
    product_name = fields.Char(string="Product")
    default_code = fields.Char(string="Default Code")
    total_quantity = fields.Float(string="Total Quantity")
    total_price = fields.Float(string="Total Price")
    nsap = fields.Float(string="Nasp")
    sales_person = fields.Many2one(comodel_name='res.users', string="Sales Person")

    last_total_quantity = fields.Float(string="Last Total Quantity")
    last_total_price = fields.Float(string="Last Total Price")
    last_nsap = fields.Float(string="Last Nasp")

    total_plan_quantity = fields.Float(string="Total Plan Quantity")
    total_plan_price = fields.Float(string="Total Plan Price")
    plan_nsap = fields.Float(string="Plan Nasp")

    qty_percentage = fields.Float(string="QTY %")
    value_percentage = fields.Float(string="Value %")

