from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class InvoiceDetailsWizard(models.TransientModel):
    _name = 'invoice.details.wizard'
    _description = 'Invoice Details'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('customer_rank', '>', 0)],
        required=True
    )

    def get_report_data(self):
        combined_data = []
        if self.date_from > self.date_to:
            raise UserError("Date From must be before Date To")

        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        moves = self.env['account.move'].search(domain)
        if moves:
            for move in moves:
                po = move.purchase_order.name if move.purchase_order else ''
                sequence = move.name
                invoice_date = move.date
                due_date = move.invoice_date_due
                amount_total = move.amount_total
                amount_residual = move.amount_residual
                paid = amount_total - amount_residual
                sales_person = move.invoice_user_id.name if move.invoice_user_id else ''

                # حساب مدة الفاتورة بالأيام (زي Odoo)
                days = 0
                if due_date:
                    days = (date.today() - due_date).days

                if move.move_type == 'out_refund':
                    amount_total = -amount_total
                    amount_residual = -amount_residual
                    paid = -paid

                combined_data.append({
                    'po': po,
                    'sequence': sequence,
                    'date': invoice_date,
                    'amount_total': amount_total,
                    'paid': paid,
                    'amount_residual': amount_residual,
                    'invoice_date': due_date,
                    'days': days,
                    'sales_person': sales_person,
                })
                combined_data = sorted(
                    combined_data,
                    key=lambda x: x.get('days', 0),
                    reverse=True
                )

        return {
            'lines': combined_data,
            'partner': self.partner_id.name,
            'date_from': self.date_from,
            'date_to': self.date_to,

        }

    def action_print_report_pdf(self):
        return self.env.ref(
            'account_statement_report.report_invoice_details'
        ).report_action(self)

