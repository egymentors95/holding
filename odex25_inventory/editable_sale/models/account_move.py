from odoo import models, fields, api, _
from datetime import date

from odoo.exceptions import UserError


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

    # def action_post(self):
    #     for move in self:
    #         total_debit = sum(move.line_ids.mapped('debit'))
    #         total_credit = sum(move.line_ids.mapped('credit'))
    #
    #         if total_debit == 0 or total_credit == 0:
    #             raise UserError(_(
    #                 "You cannot post this .\n"
    #                 "Total Debit and Total Credit must have values and cannot be zero."
    #             ))
    #
    #     return super(AccountMove, self).action_post()

    @api.constrains('line_ids', 'line_ids.debit', 'line_ids.credit', 'state')
    def _check_debit_credit_not_zero(self):
        for move in self:
            # فقط Journal Entries
            if move.move_type != 'entry':
                continue

            # نسيب Draft فاضي يتحفظ
            if not move.line_ids:
                continue

            total_debit = sum(move.line_ids.mapped('debit'))
            total_credit = sum(move.line_ids.mapped('credit'))

            if total_debit == 0 or total_credit == 0:
                raise UserError(_(
                    "You cannot save this Journal Entry.\n"
                    "Total Debit and Total Credit must have values and cannot be zero."
                ))

