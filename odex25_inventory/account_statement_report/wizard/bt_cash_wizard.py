# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError

class BtCashWizard(models.TransientModel):
    _name = 'bt.cash.wizard'
    _description = 'Customer Account Statement'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )


    def get_report_data(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError("Date From must be before Date To")

        MoveLine = self.env['account.move.line']

        ####################################
        # 1️⃣ Initial Balance قبل الفترة
        ####################################
        initial_lines = MoveLine.search([
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.is_bt_cash', '=', True),
            ('date', '<', self.date_from),
        ])

        initial_balance = sum(initial_lines.mapped('debit')) - sum(initial_lines.mapped('credit'))

        ####################################
        # 2️⃣ حركات الفترة
        ####################################
        lines = MoveLine.search([
            ('partner_id', '=', self.partner_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.is_bt_cash', '=', True),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ], order='date, move_id, sequence, id')

        combined_data = []

        ####################################
        # 3️⃣ سطر الرصيد الافتتاحي
        ####################################
        running_balance = initial_balance

        combined_data.append({
            'date': self.date_from,
            'move_type': 'رصيد افتتاحي',
            'debit': 0.0,
            'credit': 0.0,
            'balance': running_balance,
        })

        ####################################
        # 4️⃣ سطور الحركات
        ####################################
        for line in lines:
            debit = line.debit or 0.0
            credit = line.credit or 0.0

            if debit > 0:
                move_type = 'وارد'
            elif credit > 0:
                move_type = 'منصرف'
            else:
                move_type = ''

            running_balance += debit - credit

            combined_data.append({
                'date': line.date,
                'move_type': move_type,
                'name': line.name,
                'debit': debit,
                'credit': credit,
                'balance': running_balance,
            })

        ####################################
        # 5️⃣ البيانات المرسلة للتقرير
        ####################################
        return {
            'partner_name': self.partner_id.display_name,
            'partner': self.partner_id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'lines': combined_data,
            'initial_balance': initial_balance,
        }

    def action_print_report_pdf(self):
        return self.env.ref(
            'account_statement_report.report_bt_cash_action'
        ).report_action(self)

    def action_print_report_xlsx(self):
        return self.env.ref(
            'account_statement_report.report_bt_cash_xlsx_action'
        ).report_action(self)