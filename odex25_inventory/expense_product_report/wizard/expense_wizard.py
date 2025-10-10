# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ExpenseWizard(models.TransientModel):
    _name = 'expense.wizard'
    _description = 'Expense report'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    team_ids = fields.Many2many(string='Sales Persons', comodel_name='crm.team')
    account_ids = fields.Many2many(comodel_name='account.account', string='Account')

    def get_report_data(self):
        combined_data = []

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")


        # جلب كل خطوط الفواتير مرة واحدة
        # -------------------------------
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', '=', 'entry'),
            ('debit', '>', 0),
        ]
        if self.team_ids:
            domain.append(('move_id.team_id', 'in', self.team_ids.ids))
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))

        lines = self.env['account.move.line'].search(domain)



        # -------------------------------
        for expense in lines:
            print('expense', expense)
            sales_team = expense.move_id.team_id.name
            account = expense.account_id.name
            debit = expense.debit
            employee = expense.partner_id.user_ids[0].employee_id.name if expense.partner_id.user_ids else 'N/A'



            # -------- Append --------
            combined_data.append({
                'sales_team': sales_team,
                'account': account,
                'debit': debit,
                'employee': employee,

            })

        return {'combined_data': combined_data}

    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('expense_product_report.report_action_expense').report_action(self, data=data)

    def action_print_report_html(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('expense_product_report.report_action_expense_html').report_action(self, data=data)



