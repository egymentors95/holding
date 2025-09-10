from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_blocked_for_entry = fields.Boolean(
        string="أنظمة أخرى",
        help="If checked, this account cannot be selected in manual Journal Entries."
    )
