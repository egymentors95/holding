from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_journal_ids = fields.Many2many(
        'account.journal',
        string='Allowed Journals',
        help='Journals this user is allowed to use.',
        relation='account_journal_allowed_user_rel',
        column1='user_id',
        column2='journal_id',
    )

    allowed_category_ids = fields.Many2many(
        'product.category',
        string='Allowed Categories',
        help='Categories this user is allowed to access',
        relation='product_category_allowed_user_rel',
        column1='user_id',
        column2='category_id',
    )