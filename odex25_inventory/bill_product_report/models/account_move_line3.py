from odoo import fields, models


class AccountMoveLine3(models.Model):
    _name = 'account.move.line3'
    _description = 'Temporary Profitability Report Data'

    product_category = fields.Char(string="Product Category")
    product_name = fields.Char(string="Product")
    default_code = fields.Char(string="Default Code")
    total_quantity = fields.Float(string="Total Quantity")
    foc = fields.Float(string="FOC")
    total_price = fields.Float(string="Total Price")
    nsap = fields.Float(string="Nasp")
    vendor_id = fields.Many2one(comodel_name='res.partner', string="Vendor")

    # last_total_quantity = fields.Float(string="Last Total Quantity")
    # last_total_price = fields.Float(string="Last Total Price")
    # last_nsap = fields.Float(string="Last Nasp")

    plan_quantity = fields.Float(string="Plan Quantity")
    plan_value = fields.Float(string="Plan Value")
    achive = fields.Float(string="Achive %")

