from odoo import models, fields, api


class DriverDriver(models.Model):
    _name = 'driver.driver'
    _description = 'Driver'

    name = fields.Char()