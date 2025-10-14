from odoo import models, fields, api


class HrTicketRequest(models.Model):
    _inherit = 'hr.ticket.request'

    account_ids = fields.One2many('hr.mission.type.account', 'ticket_id')


