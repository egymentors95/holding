from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse', relation='warehouses_users_relation',
                                     column1='res_id', column2='warehouse_id',
                                     string='Warehouse')
    location_ids = fields.Many2many(comodel_name="stock.location", relation='locations_users_relation',
                                    column1="res_id", column2="location_id",
                                    string="Location")
    # operation_ids = fields.Many2many(comodel_name='stock.picking.type', relation='operation_users_relation',
    #                             column1='res_id', column2='operation',
    #                             string='Operation')