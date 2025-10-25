from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_name = fields.Char(string="Tax Description", compute='_compute_vat_info', store=True)
    tax_flag = fields.Char(string="Tax Type", compute='_compute_vat_info', store=True)
    type_tax_use = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('none', 'None'),
    ],compute='_compute_vat_info', store=True)
    description_note = fields.Char(string='Description_A')


    @api.depends('invoice_line_ids.tax_ids')
    def _compute_vat_info(self):
        for move in self:
            # نجمع الضرائب كلها من أسطر الفاتورة
            taxes = move.invoice_line_ids.mapped('tax_ids')

            if taxes:
                # أول ضريبة فقط
                first_tax = taxes[0]
                move.tax_name = first_tax.description or first_tax.name or ''
                move.tax_flag = first_tax.tax_flag or ''
                move.type_tax_use = first_tax.type_tax_use or 'none'
            else:
                move.tax_name = ''
                move.tax_flag = ''
                move.type_tax_use = 'none'
