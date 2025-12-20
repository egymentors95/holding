from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    user_ids = fields.Many2many(comodel_name='res.users', relation='warehouses_users_relation', column1='warehouse_id',
                                column2='res_id',
                                string='Users')
