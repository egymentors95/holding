# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError

class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Customer Account Statement'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('customer_rank', '>', 0)],
        required=True
    )

    def _get_aging(self):
        self.ensure_one()
        today = self.date_to
        buckets = {
            '0_30': 0.0, '31_60': 0.0, '61_90': 0.0,
            '91_120': 0.0, '121_150': 0.0, '150_plus': 0.0,
        }

        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_type', '=', 'receivable'),
            ('reconciled', '=', False),
        ]
        lines = self.env['account.move.line'].search(domain)

        for line in lines:
            due_date = line.move_id.invoice_date_due or line.date
            days = (today - due_date).days
            balance = line.amount_residual
            if days <= 30:
                buckets['0_30'] += balance
            elif days <= 60:
                buckets['31_60'] += balance
            elif days <= 90:
                buckets['61_90'] += balance
            elif days <= 120:
                buckets['91_120'] += balance
            elif days <= 150:
                buckets['121_150'] += balance
            else:
                buckets['150_plus'] += balance
        return buckets

    def get_report_data(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError("Date From must be before Date To")

        MoveLine = self.env['account.move.line']

        # Initial balance
        init_lines = MoveLine.search([
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('date', '<', self.date_from),
            ('account_id.internal_type', 'in', ('receivable', 'payable')),
        ])
        initial_balance = sum(init_lines.mapped(lambda l: l.debit - l.credit))

        # Period lines
        lines = MoveLine.search([
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.internal_type', 'in', ('receivable', 'payable')),
        ], order='date, move_id, sequence, id')

        running_balance = initial_balance
        total_debit = 0.0
        total_credit = 0.0
        combined_data = []

        # Initial row
        combined_data.append({
            'date': self.date_from,
            'description': 'رصيد أول المدة',
            'document': '', 'sequence': '',
            'debit': 0.0, 'credit': 0.0,
            'balance': running_balance,
        })

        for line in lines:
            running_balance += line.debit - line.credit
            total_debit += line.debit
            total_credit += line.credit
            combined_data.append({
                'date': line.date,
                'description': line.name or line.move_id.ref or '',
                'document': line.move_id.name,
                'sequence': line.move_id.name,
                'debit': line.debit,
                'credit': line.credit,
                'balance': running_balance,
            })

        return {
            'partner_name': self.partner_id.display_name,
            'partner': self.partner_id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'initial_balance': initial_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'ending_balance': running_balance,
            'lines': combined_data,
            'aging': self._get_aging(),
        }

    def action_print_report_pdf(self):
        return self.env.ref(
            'account_statement_report.report_customer_statement'
        ).report_action(self)