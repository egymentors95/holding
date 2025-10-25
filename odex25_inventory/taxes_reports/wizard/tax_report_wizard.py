# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class TaxReportWizard(models.TransientModel):
    _name = 'tax.report.wizard'
    _description = 'Tax Report'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def get_report_data(self):
        combined_data = []

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("Date From must be before or equal to Date To."))

        # -----------------------------------
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('state', '=', 'posted'),

        ]
        invoices = self.env['account.move'].search(domain)


        # -----------------------------------
        for invoice in invoices:
            tax_flag = invoice.tax_flag
            source = invoice.type_tax_use
            tax_value = invoice.amount_tax if invoice.move_type in ['out_invoice','out_refund','in_invoice','in_refund'] else invoice.tax_value
            tax_name = invoice.e_amount_tax
            value = invoice.amount_untaxed if invoice.move_type in ['out_invoice','out_refund','in_invoice','in_refund'] else invoice.amount_untaxed_entry
            invoice_name = invoice.name
            date = invoice.date
            description_note = invoice.description_note
            code = invoice.partner_id.ref
            partner_name = invoice.partner_id.name
            partner_vat = invoice.partner_id.vat


            combined_data.append({
                'tax_flag': tax_flag,
                'source': source,
                'tax_value': tax_value,
                'tax_name': tax_name,
                'value': value,
                'date': date,
                'description_note': description_note,
                'code': code,
                'partner_name': partner_name,
                'partner_vat': partner_vat,
                'invoice_name': invoice_name,

            })

        return {'combined_data': sorted(combined_data, key=lambda inv: inv['source'] or '')}

    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'invoices': self.get_report_data()['combined_data'],
        }
        return self.env.ref('taxes_reports.report_action_tax').report_action(self, data=data)




