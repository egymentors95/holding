from odoo import models, _
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_blocked_accounts(self):
        for line in self:
            if line.move_id.move_type == 'entry' and line.account_id.is_blocked_for_entry:
                raise UserError(
                    _("You cannot use the account '%s' in manual Journal Entries.")
                    % line.account_id.display_name
                )

    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_blocked_accounts()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._check_blocked_accounts()
        return res
