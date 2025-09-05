from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_event_address = fields.Boolean(string="Event address")
    is_organizer = fields.Boolean(string="Organizer")
    is_sponsor = fields.Boolean(string="Sponsor")
    contact_person = fields.Char(string="Contact person")
