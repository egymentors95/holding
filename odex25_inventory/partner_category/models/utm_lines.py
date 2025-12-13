from odoo import models, fields, api


class UTMLines(models.Model):
    _name = 'utm.lines'
    _description = 'UTM Lines'

    product_template_id = fields.Many2one(comodel_name='product.template', string='Product Template')
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')

