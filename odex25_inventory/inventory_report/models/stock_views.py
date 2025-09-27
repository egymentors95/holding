from odoo import fields, models


class AccountMoveLine3(models.Model):
    _name = 'stock.views'
    _description = 'Stock'

    product_category = fields.Char(string="Product Category")
    product_name = fields.Char(string="Product")
    default_code = fields.Char(string="Default Code")
    Lots = fields.Char(string='Serial Number')
    on_hand_qty = fields.Float(string='QTY')
    sold_last_6_months = fields.Float(string='QTY last 6m')
    avg_sold_last_6_months = fields.Float(string='QTY Avg')
    equ_month = fields.Float(string='QTY/month')
    naap = fields.Float(string='NAAP')
    value = fields.Float(string='Value')


