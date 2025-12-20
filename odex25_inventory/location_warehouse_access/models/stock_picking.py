from odoo import models, fields
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # location_dest_id = fields.Many2one(
    #     comodel_name='stock.location', string="Destination Location",
    #     compute="_compute_location_id", store=True, precompute=True, readonly=False,
    #     check_company=True, required=True,
    #     domain="[('user_ids','in',[uid])]",
    #     states={'done': [('readonly', True)]})
    #
    # location_id = fields.Many2one(
    #     comodel_name='stock.location', string="Source Location",
    #     domain="[('user_ids','in',[uid])]",
    #     compute="_compute_location_id", store=True, precompute=True, readonly=False,
    #     check_company=True, required=True,
    #     states={'done': [('readonly', True)]})
    #
    # picking_type_id = fields.Many2one(
    #     'stock.picking.type', 'Operation Type',
    #     domain="[('user_ids','in',[uid])]",
    #     required=True, readonly=True, index=True,
    #     states={'draft': [('readonly', False)]})

# class InheritStockPickingType(models.Model):
#     _inherit = 'stock.picking.type'
#
#     user_ids = fields.Many2many(comodel_name='res.users', relation='operation_users_relation',
#                                 column1='operation', column2='res_id',
#                                 string='Users')
