from odoo import models, fields, api
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_total_in_words_ar = fields.Char(
        string='Amount in Words (Arabic)',
        compute='_compute_amount_in_words_ar',
        store=True
    )

    @api.depends('amount_total')
    def _compute_amount_in_words_ar(self):
        for move in self:
            amount = move.amount_total

            integer_part = int(amount)
            decimal_part = int(round((amount - integer_part) * 100))

            # الجزء الصحيح
            words = num2words(integer_part, lang='ar')
            words += " ريال"

            # الهللات
            if decimal_part > 0:
                words += " و "
                words += num2words(decimal_part, lang='ar')
                words += " هللة"

            words += " فقط لا غير"

            move.amount_total_in_words_ar = words
