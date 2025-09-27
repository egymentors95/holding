from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if move.move_type == 'entry':
                errors = []

                # تحقق من شركاء الحسابات
                partner_lines = move.line_ids.filtered(
                    lambda l: l.account_id.is_partner and not l.partner_id
                )
                for line in partner_lines:
                    errors.append(f"Please insert Partner for account '{line.account_id.name}'")

                # تحقق من التحليلات
                analytic_lines = move.line_ids.filtered(
                    lambda l: l.account_id.is_analytic and not l.analytic_tag_ids
                )
                for line in analytic_lines:
                    errors.append(f"Please insert Analytic tag for account '{line.account_id.name}'")

                if errors:
                    raise UserError("\n".join(errors))

        # بعد التحقق، استدعي السلوك الأصلي
        return super(AccountMove, self).action_post()



