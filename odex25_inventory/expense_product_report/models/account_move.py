from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    team_id = fields.Many2one('crm.team', string='Sales Team', tracking=True)
    partner_category_id = fields.Many2one(comodel_name='partner.category', string='Partner Category', compute='_compute_partner_category', store=True)
    tax_name = fields.Char(string="Tax Description", compute='_compute_vat_info', store=True)
    tax_flag = fields.Char(string="Tax Type", compute='_compute_vat_info', store=True)
    e_amount_tax = fields.Char(string="E Amount Tax", compute='_compute_vat_info', store=True)
    type_tax_use = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('none', 'None'),
    ], compute='_compute_vat_info', store=True)
    tax_value = fields.Float(string="Tax Value", compute='_compute_tax_amounts', store=True)
    amount_untaxed_entry = fields.Float(string="Untaxed Amount", compute='_compute_tax_amounts', store=True)


    @api.depends('invoice_line_ids.tax_ids', 'line_ids.tax_ids')
    def _compute_vat_info(self):
        for move in self:
            # -------------------------------
            if move.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                taxes = move.invoice_line_ids.mapped('tax_ids')
                if taxes:
                    first_tax = taxes[0]
                    move.tax_name = first_tax.description or first_tax.name or ''
                    move.e_amount_tax = first_tax.amount or ''
                    move.tax_flag = getattr(first_tax, 'tax_flag', '')
                    move.type_tax_use = getattr(first_tax, 'type_tax_use', 'none')
                else:
                    move.tax_name = ''
                    move.tax_flag = ''
                    move.e_amount_tax = ''
                    move.type_tax_use = 'none'

            # -------------------------------
            # القيود المحاسبية
            elif move.move_type == 'entry':
                tax_line = next(
                    (line for line in move.line_ids if line.tax_ids),
                    False
                )
                if tax_line:
                    first_tax = tax_line.tax_ids[0]
                    move.tax_name = first_tax.description or first_tax.name or ''
                    move.e_amount_tax = first_tax.amount or ''
                    move.tax_flag = getattr(first_tax, 'tax_flag', '')
                    move.type_tax_use = getattr(first_tax, 'type_tax_use', 'none')
                else:
                    move.tax_name = ''
                    move.tax_flag = ''
                    move.e_amount_tax = ''
                    move.type_tax_use = 'none'

    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.tax_ids')
    def _compute_tax_amounts(self):
        for move in self:
            untaxed_total = 0.0
            tax_total = 0.0
            tax_rate = 0.0

            # بنجمع إجمالي بدون الضريبة + بنجيب أول نسبة ضريبة موجودة
            for line in move.line_ids:
                balance = line.debit - line.credit
                if not line.tax_ids:
                    untaxed_total += balance
                else:
                    # أول ضريبة فقط (لو في أكثر من واحدة)
                    if not tax_rate:
                        first_tax = line.tax_ids[0]
                        tax_rate = first_tax.amount or 0.0

            # نحسب قيمة الضريبة بناءً على النسبة
            tax_total = untaxed_total * (tax_rate / 100.0)

            move.amount_untaxed_entry = abs(untaxed_total)
            move.tax_value = abs(tax_total)



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
                    lambda l: l.account_id.is_analytic and not l.analytic_account_id
                )
                for line in analytic_lines:
                    errors.append(f"Please insert Analytic account for account '{line.account_id.name}'")

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



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_partner = fields.Boolean(compute="get_is_partner", store=True)
    is_analytic = fields.Boolean(compute="get_is_account", store=True)

    @api.depends('account_id', 'account_id.is_partner')
    def get_is_partner(self):
        for rec in self:
            if rec.account_id.is_partner:
                rec.is_partner = True
            else:
                rec.is_partner = False

    @api.depends('account_id', 'account_id.is_analytic')
    def get_is_account(self):
        for rec in self:
            if rec.account_id.is_analytic:
                rec.is_analytic = True
            else:
                rec.is_analytic = False
