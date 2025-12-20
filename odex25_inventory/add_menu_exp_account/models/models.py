# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


@api.depends('restrict_mode_hash_table', 'state')
def _compute_show_reset_to_draft_button(self):
    for move in self:
        move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in ('posted', 'cancel')


class Expense(models.Model):
    _name = 'expense.expense'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'expense_expense'
    _rec_name = 'seq'

    name = fields.Text(string="Ref", required=False, )
    journal_entry_id = fields.Many2one(comodel_name="account.move", string="Journal Entry", copy=False)
    expense_date = fields.Date(string="Expense Date", required=False, tracking=True)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True, tracking=True,
                                 domain="[('type', 'in', ['bank','cash'])]")
    expenses_ids = fields.One2many(comodel_name="expense.line", inverse_name="invoice_id", string="Expenses",
                                   tracking=True)
    total = fields.Float(string="Total", tracking=True)
    tax = fields.Float(string="Taxes", compute="_get_tax", tracking=True, store=True)
    state = fields.Selection(selection=
                             [
                                 ('draft', 'Draft'),
                                 ('to_manager', 'To Manager'),
                                 ('to_financial_manager', 'To Financial Manager'),
                                 ('to_account', 'To Account'),
                                ('confirm', 'Posted'),
                              ], required=False, default='draft', tracking=True)
    amount_taxed = fields.Float(string="Un Taxed Amount", tracking=True)
    seq = fields.Char(readonly=True, copy=False, )
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)

    def unlink(self):
        error_message = _('You cannot delete a expense which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(Expense, self).unlink()

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.journal_entry_id.button_draft()


    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code(
                'expense.sequence', ) or _('New')
        result = super(Expense, self).create(vals)
        return result

    def submit_to_manager(self):
        for rec in self:
            rec.state = 'to_manager'

    def submit_to_financial_manager(self):
        for rec in self:
            rec.state = 'to_financial_manager'

    def submit_to_account(self):
        for rec in self:
            rec.state = 'to_account'


    def get_confirm(self):
        for rec in self:
            lines = []
            taxx = 0
            analytic_var = False
            for line in rec.expenses_ids:
                employee = line.employee_id.name
                partner = line.partner_id.id
                if line.analytic_account_id:
                    analytic_var = line.analytic_account_id.id
                for tax in line.tax_ids.invoice_repartition_line_ids:
                    if tax.account_id:
                        taxx = tax.account_id.id
                lines.append([0, 0, {
                    'account_id': line.account_id.id,
                    'name': employee,
                    'debit': line.price_subtotal,
                    'analytic_account_id': analytic_var,
                    'partner_id': partner,

                }])
            if taxx:
                lines.append([0, 0, {
                    'account_id': taxx,
                    'name': f'{employee}\n(tax)',
                    'debit': rec.tax,
                    'analytic_account_id': analytic_var,
                    'partner_id': partner,

                }])
            lines.append([0, 0, {
                'account_id': rec.journal_id.default_account_id.id,
                'name': f'{employee}\n{rec.name}',
                'credit': rec.total,
                'analytic_account_id': analytic_var,
                'partner_id': partner,

            }])

            if rec.journal_entry_id.is_created == False:
                invoice = self.env['account.move'].sudo().create({
                    'is_created': True,
                    'move_type': 'entry',
                    'ref': rec.seq,
                    'date': rec.expense_date,
                    'journal_id': rec.journal_id.id,
                    'line_ids': lines,
                })
                rec.journal_entry_id = invoice.id
                invoice.action_post()

            else:
                rec.journal_entry_id.date = rec.expense_date
                rec.journal_entry_id.journal_id = rec.journal_id
                rec.journal_entry_id.ref = rec.name
                rec.journal_entry_id.line_ids = False
                rec.journal_entry_id.line_ids = lines
                rec.journal_entry_id.action_post()
            rec.state = 'confirm'

    @api.depends("expenses_ids.tax_ids")
    def _get_tax(self):
        subtotal = 0
        for rec in self:
            n = 0
            taxes = 0
            for line in rec.expenses_ids:
                t = 0
                for any_line in line.tax_ids:
                    t = t + any_line.amount
                taxes = (t / 100) * line.quantity * line.price_unit
                line.price_subtotal = line.quantity * line.price_unit
                subtotal = subtotal + line.price_subtotal
                n = n + taxes
            rec.tax = n
            rec.amount_taxed = subtotal
            rec.total = rec.tax + rec.amount_taxed


class ExpenseLine(models.Model):
    _name = 'expense.line'
    _description = 'expense_line'

    invoice_id = fields.Many2one(comodel_name="expense.expense", )
    company_id = fields.Many2one(related='invoice_id.company_id', store=True)
    employee_id = fields.Many2one(comodel_name='hr.employee')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', compute='_get_partner_id', store=True)
    product_ids = fields.Many2one(comodel_name="product.product", string="Product", )
    name = fields.Char(string="Label", )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=True,
                                 related='product_ids.property_account_expense_id', readonly=False, store=True)
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account ",
                                          required=False, )
    quantity = fields.Float(string="Quantity", required=False, default="1")
    price_unit = fields.Float(string="Price", required=True, )
    tax_ids = fields.Many2many(comodel_name="account.tax", string="Taxes", )
    price_subtotal = fields.Float(string="Subtotal", required=False, )
    vat_value = fields.Float(string='Vat Value', compute='_get_total_vat', store=True)
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments', )


    @api.depends('price_subtotal', 'tax_ids')
    def _get_total_vat(self):
        for rec in self:
            t = 0
            for any_line in rec.tax_ids:
                t = t + any_line.amount
            taxes = (t / 100) * rec.price_subtotal
            rec.vat_value = taxes

    @api.depends('employee_id')
    def _get_partner_id(self):
        for rec in self:
            if not rec.partner_id:
                if rec.employee_id and rec.employee_id.user_partner_id:
                    rec.partner_id = rec.employee_id.user_partner_id.id



# class PartnerExpenses(models.Model):
#     _inherit = 'res.partner'
#
#     is_expenses = fields.Boolean()
#
#
# class AccountJournalExpenses(models.Model):
#     _inherit = 'account.journal'
#
#     expenses_filtration = fields.Boolean(string="Expenses Filtration")
#     for_expenses = fields.Boolean(string="For Expenses")
#
#
class AccountMoveExpenses(models.Model):
    _inherit = 'account.move'

    is_expenses = fields.Boolean()
    is_created = fields.Boolean(string="", default=False)
    # journal_payment_id = fields.Many2one(comodel_name="account.journal")
    # expenses_filtration = fields.Boolean(string="Expenses Filtration", related='journal_payment_id.expenses_filtration')

    # @api.model
    # def create(self, vals_list):
    #     res = super(AccountMoveExpenses, self).create(vals_list)
    #     for rec in res:
    #         if rec.is_expenses:
    #             partner = self.env['res.partner'].search([('is_expenses', '=', True)], limit=1)
    #             if not partner:
    #                 raise ValidationError('Please Add Expenses Partner First')
    #             rec.partner_id = partner.id
    #     return res

    # def action_post(self):
    #     res = super(AccountMoveExpenses, self).action_post()
    #     for rec in self:
    #         if rec.is_expenses:
    #             if not rec.journal_payment_id:
    #                 raise ValidationError('Please Select Journal Payment First')
    #             for line in rec.line_ids:
    #                 line.date = rec.date
    #             for line in rec.invoice_line_ids:
    #                 line.date = rec.date
    #             self.env['account.payment.register'].with_context(active_model='account.move',
    #                                                               active_ids=rec.ids).create(
    #                 {'journal_id': rec.journal_payment_id.id, 'payment_date': rec.date})._create_payments()
    #     return res
