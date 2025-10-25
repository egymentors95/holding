from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_name = fields.Char(string="Tax Description", compute='_compute_vat_info', store=True)
    tax_flag = fields.Char(string="Tax Type", compute='_compute_vat_info', store=True)
    e_amount_tax = fields.Char(string="E Amount Tax", compute='_compute_vat_info', store=True)
    type_tax_use = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('none', 'None'),
    ],compute='_compute_vat_info', store=True)
    description_note = fields.Char(string='Description_A')
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
                    move.e_amount_tax = first_tax.amount  or ''
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
                    move.e_amount_tax = first_tax.amount  or ''
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




