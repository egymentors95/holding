from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    selection_type = fields.Selection(
        selection=[
            ('view', 'View'),
            ('else', 'Else'),
            ],compute='_compute_selection_type', store=True)
    is_bt_cash = fields.Boolean(string='is Bt Cash')

    @api.depends('user_type_id')
    def _compute_selection_type(self):
        for record in self:
            if record.user_type_id and record.user_type_id.type in ['view']:
                record.selection_type = 'view'
            else:
                record.selection_type = 'else'
