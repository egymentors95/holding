from odoo import fields, models


class Sponsor(models.Model):
    _inherit = "event.sponsor"

    contact_person = fields.Char(string="Partner contact person", related="partner_id.contact_person")
