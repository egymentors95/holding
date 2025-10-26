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
            sales_team = expense.move_id.team_id.name
            account = expense.account_id.name
            debit = expense.debit
            # employee = expense.move_id.invoice_user_id.employee_id.name if expense.move_id.invoice_user_id else 'N/A'
            employee = expense.partner_id.user_ids[0].employee_id.name if expense.partner_id.user_ids else 'N/A'


            # -------- Append --------
            combined_data.append({
                'sales_team': sales_team,
                'account': account,
                'debit': debit,
                'employee': employee,
            })

        # جلب بيانات المبيعات
        sales_data = self.get_sales_data()

        return {
            'combined_data': combined_data,
            'sales_data': sales_data  # إضافة بيانات المبيعات
        }

    def get_sales_data(self):
        """جلب بيانات المبيعات لكل موظف"""
        sales_domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_group', '=', 'income'),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]

        if self.team_ids:
            sales_domain.append(('move_id.team_id', 'in', self.team_ids.ids))

        sales_lines = self.env['account.move.line'].search(sales_domain)
        print('sales_lines', sales_lines)

        # تجميع بيانات المبيعات لكل موظف
        data_by_employee = {}
        total_sales = 0.0
        total_cost = 0.0

        for line in sales_lines:
            employee = line.move_id.invoice_user_id.employee_id.name if line.move_id.invoice_user_id else 'N/A'
            # employee = line.partner_id.user_ids[0].employee_id.name if line.partner_id.user_ids else 'N/A'

            # حساب صافي المبيعات (الإيراد)
            qty = line.quantity or 0.0
            sales_amount = line.price_subtotal or 0.0
            cost_amount = line.product_id.standard_price * qty  # تكلفة المنتج

            if employee not in data_by_employee:
                data_by_employee[employee] = {
                    'sales': 0.0,
                    'cost': 0.0,
                    'net_profit': 0.0,
                }

            data_by_employee[employee]['sales'] += sales_amount
            data_by_employee[employee]['cost'] += cost_amount
            data_by_employee[employee]['net_profit'] = (
                    data_by_employee[employee]['sales'] - data_by_employee[employee]['cost']
            )

            total_sales += sales_amount
            total_cost += cost_amount

        total_net_profit = total_sales - total_cost

        return {
            'by_employee': data_by_employee,
            'total_sales': total_sales,
            'total_cost': total_cost,
            'total_net_profit': total_net_profit,
        }
    def action_print_report_xlsx(self):
        self.ensure_one()
        report_data = self.get_report_data()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': report_data['combined_data'],
            'sales_data': report_data['sales_data'],  # إضافة بيانات المبيعات
        }
        return self.env.ref('expense_product_report.report_action_expense').report_action(self, data=data)

    def action_print_report_html(self):
        self.ensure_one()
        report_data = self.get_report_data()  # استخدم نفس دالة get_report_data
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': report_data['combined_data'],
            'sales_data': report_data['sales_data'],  # إضافة بيانات المبيعات
        }
        return self.env.ref('expense_product_report.report_action_expense_html').report_action(self, data=data)



