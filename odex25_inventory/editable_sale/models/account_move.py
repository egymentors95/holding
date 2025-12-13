from odoo import models, fields, api
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date(
        string='Invoice/Bill Date',
        readonly=True,
        index=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        default=lambda self: date.today(),
    )
