from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    team_id = fields.Many2one('crm.team', string='Sales Team', tracking=True)
    partner_category_id = fields.Many2one(comodel_name='partner.category', string='Partner Category', compute='_compute_partner_category', store=True)

    @api.depends('partner_id', 'partner_id.category_id')
    def _compute_partner_category(self):
        for move in self:
            move.partner_category_id = move.partner_id.partner_category.id if move.partner_id else False

    def server_action_partner_category(self):
        for move in self:
            if move.partner_id:
                move.partner_category_id = move.partner_id.partner_category.id
            else:
                move.partner_category_id = False

    def _check_move_lines_validations(self):
        """تتحقق من الشروط الخاصة بخطوط القيد."""
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

    def write(self, vals):
        """ننفذ التحقق عند أي تعديل."""
        res = super(AccountMove, self).write(vals)
        self._check_move_lines_validations()
        return res

    @api.model
    def create(self, vals):
        """ننفذ التحقق عند الإنشاء."""
        move = super(AccountMove, self).create(vals)
        move._check_move_lines_validations()
        return move



