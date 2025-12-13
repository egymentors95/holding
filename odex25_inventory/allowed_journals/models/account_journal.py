from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    allowed_user_ids = fields.Many2many(
        'res.users',
        string='Allowed Users',
        help='Users allowed to use this journal.',
        relation='account_journal_allowed_user_rel',
        column1='journal_id',
        column2='user_id',
    )