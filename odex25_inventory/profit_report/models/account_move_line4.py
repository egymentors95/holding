from odoo import fields, models


class AccountMoveLine4(models.Model):
    _name = 'account.move.line4'
    _description = 'Account Move Line4'

    product_category = fields.Char(string="Product Category")
    product_name = fields.Char(string="Product")
    default_code = fields.Char(string="Default Code")
    total_quantity = fields.Float(string="Total Quantity")
    total_price = fields.Float(string="Total Price")
    nsap = fields.Float(string="NASP")

    last_total_quantity = fields.Float(string="Last Total Quantity")
    last_total_price = fields.Float(string="Last Total Price")
    last_nsap = fields.Float(string="Last NASP")

    naap = fields.Float(string="NAPP")
    last_year_naap = fields.Float(string="Last Year NAPP")

    margin = fields.Float(string="Margin")
    last_margin = fields.Float(string="Last Margin")

    profit_value = fields.Float(string="Profit Value")
    last_profit_value = fields.Float(string="Last Profit Value")


