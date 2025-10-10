from odoo import models, api

class ExpenseReportHtml(models.AbstractModel):
    _name = 'report.expense_product_report.expense_report_html'
    _description = 'Expense HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        combined_data = data.get('product_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        # 1️⃣ تأكد من وجود موظف
        for rec in combined_data:
            if not rec.get('employee'):
                rec['employee'] = 'N/A'

        # 2️⃣ استخراج الموظفين
        employees = sorted(set([rec['employee'] for rec in combined_data if rec.get('employee')]))

        # 3️⃣ تجميع البيانات حسب الفريق والحساب
        grouped = {}
        for rec in combined_data:
            team = rec.get('sales_team') or 'No Team'
            account = rec.get('account') or 'No Account'
            employee = rec.get('employee') or 'N/A'
            debit = rec.get('debit') or 0.0

            grouped.setdefault(team, {})
            grouped[team].setdefault(account, {emp: 0.0 for emp in employees})
            grouped[team][account].setdefault('total', 0.0)

            grouped[team][account][employee] += debit
            grouped[team][account]['total'] += debit

        # 4️⃣ حساب Grand Total
        grand_totals = {emp: 0.0 for emp in employees}
        grand_totals['total'] = 0.0
        for team in grouped.values():
            for acc_data in team.values():
                for emp in employees:
                    grand_totals[emp] += acc_data.get(emp, 0.0)
                grand_totals['total'] += acc_data['total']

        # 5️⃣ حساب Achieve% لكل حساب
        grand_total_value = grand_totals['total'] or 1.0  # عشان ما يقسمش على صفر
        for team in grouped:
            for acc_name, acc_data in grouped[team].items():
                acc_data['achieve'] = (acc_data['total'] / grand_total_value) * 100.0

        return {
            'date_from': date_from,
            'date_to': date_to,
            'employees': employees,
            'grouped': grouped,
            'grand_totals': grand_totals,
        }

