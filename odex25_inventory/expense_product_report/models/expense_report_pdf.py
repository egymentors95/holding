from odoo import models, api

class ExpenseReportHtml(models.AbstractModel):
    _name = 'report.expense_product_report.expense_report_html'
    _description = 'Expense HTML Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        lots_data = data.get('product_ids', [])
        sales_data = data.get('sales_data', {})  # جلب بيانات المبيعات
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        grouped_data = {}
        employees = set()

        # --- تجميع البيانات ---
        for rec in lots_data:
            team = rec.get('sales_team') or 'No Team'
            account = rec.get('account')
            employee = rec.get('employee') or 'N/A'
            debit = rec.get('debit') or 0.0

            employees.add(employee)
            grouped_data.setdefault(team, {})
            grouped_data[team].setdefault(account, {'employees': {}, 'total': 0.0})
            grouped_data[team][account]['employees'][employee] = (
                grouped_data[team][account]['employees'].get(employee, 0.0) + debit
            )
            grouped_data[team][account]['total'] += debit

        # إضافة الموظفين من بيانات المبيعات
        sales_by_employee = sales_data.get('by_employee', {})
        for employee in sales_by_employee.keys():
            employees.add(employee)

        employees = sorted(list(employees))

        # --- حساب الإجماليات ---
        grand_totals = {emp: 0.0 for emp in employees}
        grand_totals['total'] = 0.0
        team_summaries = {}

        for team, accounts in grouped_data.items():
            team_total_sum = 0.0
            team_totals = {emp: 0.0 for emp in employees}

            for acc, acc_data in accounts.items():
                for emp in employees:
                    val = acc_data['employees'].get(emp, 0.0)
                    team_totals[emp] += val
                    grand_totals[emp] += val
                team_total_sum += acc_data['total']
                grand_totals['total'] += acc_data['total']

            team_totals['total'] = team_total_sum
            team_summaries[team] = team_totals

        # --- حساب Achieve كنسبة من Grand Total ---
        total_val = grand_totals.get('total', 0.0)
        for team, team_totals in team_summaries.items():
            team_achieve = {}
            for emp in employees:
                team_achieve[emp] = (team_totals[emp] / total_val * 100) if total_val else 0
            team_achieve['total'] = (team_totals['total'] / total_val * 100) if total_val else 0
            team_summaries[team]['achieve'] = team_achieve

        return {
            'date_from': date_from,
            'date_to': date_to,
            'grouped': grouped_data,
            'employees': employees,
            'grand_totals': grand_totals,
            'team_summaries': team_summaries,
            'sales_data': sales_data,  # إضافة بيانات المبيعات
        }