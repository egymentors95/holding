from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource
from xlsxwriter.utility import xl_rowcol_to_cell


class ExpenseReport(models.AbstractModel):
    _name = 'report.expense_product_report.expense_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('product_ids', [])
        sales_data = data.get('sales_data', {})  # جلب بيانات المبيعات
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        worksheet = workbook.add_worksheet('Expense Report')
        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:Z', 15)

        # ======= تنسيقات =======
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#D9E1F2', 'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00',})
        subtotal_format = workbook.add_format(
            {'bold': True, 'bg_color': '#FCE4D6', 'align': 'center', 'valign': 'vcenter', 'border': 1,'num_format': '#,##0.00',})
        grand_total_format = workbook.add_format(
            {'bold': True, 'bg_color': '#C6E0B4', 'align': 'center', 'valign': 'vcenter', 'border': 1,'num_format': '#,##0.00',})
        sales_total_format = workbook.add_format(
            {'bold': True, 'bg_color': '#FFE699', 'align': 'center', 'valign': 'vcenter', 'num_format': '#,##0.00',
             'border': 1})  # تنسيق جديد للمبيعات
        percent_format = workbook.add_format(
            {'num_format': '0.00%', 'align': 'center', 'valign': 'vcenter', 'border': 1,'num_format': '#,##0.00',})

        # ======= اللوجو =======
        logo_path = get_module_resource('expense_product_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 6, logo_path, {'x_scale': 0.9, 'y_scale': 0.2})

        row = 0
        worksheet.write(row, 0, "Report:", header_format)
        worksheet.write(row, 1, "Expense Report", cell_format)
        row += 1
        worksheet.write(row, 0, "Date From:", header_format)
        worksheet.write(row, 1, str(date_from or ''), cell_format)
        row += 1
        worksheet.write(row, 0, "Date To:", header_format)
        worksheet.write(row, 1, str(date_to or ''), cell_format)
        row += 1
        worksheet.write(row, 0, "Currency:", header_format)
        worksheet.write(row, 1, "SR or USD", cell_format)
        row += 2

        # ======= تجهيز البيانات =======
        grouped_data = {}
        employees = set()
        for rec in lots_data:
            team = rec.get('sales_team') or 'No Team'
            account = rec.get('account')
            employee = rec.get('employee') or 'N/A'
            debit = rec.get('debit') or 0.0

            employees.add(employee)
            grouped_data.setdefault(team, {})
            grouped_data[team].setdefault(account, {'employees': {}, 'total': 0.0})
            grouped_data[team][account]['employees'][employee] = grouped_data[team][account]['employees'].get(employee,
                                                                                                              0.0) + debit
            grouped_data[team][account]['total'] += debit

        # إضافة الموظفين من بيانات المبيعات أيضاً
        sales_by_employee = sales_data.get('by_employee', {})
        for employee in sales_by_employee.keys():
            employees.add(employee)

        employees = sorted(list(employees))
        emp_col_map = {emp: idx + 2 for idx, emp in enumerate(employees)}
        total_col = 2 + len(employees)
        percent_col = total_col + 1

        # ======= عناوين الأعمدة =======
        worksheet.write(row, 0, 'Team', header_format)
        worksheet.write(row, 1, 'Account', header_format)
        for emp in employees:
            worksheet.write(row, emp_col_map[emp], emp, header_format)
        worksheet.write(row, total_col, 'Total', header_format)
        worksheet.write(row, percent_col, 'Achieve %', header_format)
        row += 1

        # ======= إعداد القيم الإجمالية =======
        grand_totals = {emp: 0.0 for emp in employees}
        grand_totals['total'] = 0.0
        teams_summary = []  # لتخزين نتائج كل فريق

        # ======= كتابة البيانات =======
        for team, accounts in grouped_data.items():
            worksheet.merge_range(row, 0, row, percent_col, team, bold)
            row += 1
            team_totals = {emp: 0.0 for emp in employees}
            team_totals['total'] = 0.0

            for account, acc_data in accounts.items():
                worksheet.write(row, 0, '', cell_format)
                worksheet.write(row, 1, account, cell_format)

                for emp in employees:
                    val = acc_data['employees'].get(emp, 0.0)
                    worksheet.write_number(row, emp_col_map[emp], val, cell_format)
                    team_totals[emp] += val
                    grand_totals[emp] += val

                total_val = acc_data['total']
                worksheet.write_number(row, total_col, total_val, cell_format)
                worksheet.write(row, percent_col, '', percent_format)
                team_totals['total'] += total_val
                grand_totals['total'] += total_val
                row += 1

            # subtotal
            worksheet.write(row, 0, f"Subtotal", subtotal_format)
            worksheet.write(row, 1, '', subtotal_format)
            for emp in employees:
                worksheet.write_number(row, emp_col_map[emp], team_totals[emp], subtotal_format)
            worksheet.write_number(row, total_col, team_totals['total'], subtotal_format)
            worksheet.write(row, percent_col, '', subtotal_format)
            row += 1

            # نحجز مكان صف Achieve لاحقاً
            achieve_row = row
            row += 1
            teams_summary.append((achieve_row, team, team_totals))

        # ======= Grand Total =======
        worksheet.write(row, 0, 'Grand Total', grand_total_format)
        worksheet.write(row, 1, '', grand_total_format)
        for emp in employees:
            worksheet.write_number(row, emp_col_map[emp], grand_totals[emp], grand_total_format)
        worksheet.write_number(row, total_col, grand_totals['total'], grand_total_format)
        worksheet.write_number(row, percent_col, 1, percent_format)
        grand_total_val = grand_totals['total']
        row += 1

        # ======= Total Sales (Net Profit) =======
        worksheet.write(row, 0, 'Total Gross Profit', sales_total_format)
        worksheet.write(row, 1, '', sales_total_format)

        total_net_profit = 0.0
        for emp in employees:
            # استخدام net_profit بدل sales_val
            net_profit_val = sales_by_employee.get(emp, {}).get('net_profit', 0.0)
            worksheet.write_number(row, emp_col_map[emp], net_profit_val, sales_total_format)
            total_net_profit += net_profit_val

        worksheet.write_number(row, total_col, total_net_profit, sales_total_format)
        worksheet.write(row, percent_col, '', sales_total_format)
        row += 1

        # ======= حساب Achieve % للصفوف =======
        current_row = 6  # أول صف فعلي بعد العناوين
        for team, accounts in grouped_data.items():
            current_row += 1  # تخطي صف الفريق
            for account, acc_data in accounts.items():
                total_val = acc_data['total']
                achieve = (total_val / grand_total_val) if grand_total_val else 0
                worksheet.write_number(current_row, percent_col, achieve, percent_format)
                current_row += 1
            current_row += 2  # تخطي subtotal + سطر Achieve

        # ======= حساب صف Achieve لكل Team =======
        for team_row, team_name, team_totals in teams_summary:
            worksheet.write(team_row, 0, f"Achieve %", subtotal_format)
            worksheet.write(team_row, 1, '', subtotal_format)
            for emp in employees:
                emp_team_val = team_totals.get(emp, 0.0)
                achieve_val = (emp_team_val / grand_total_val) if grand_total_val else 0
                worksheet.write_number(team_row, emp_col_map[emp], achieve_val, percent_format)
            total_achieve = (team_totals['total'] / grand_total_val) if grand_total_val else 0
            worksheet.write_number(team_row, total_col, total_achieve, percent_format)
            worksheet.write(team_row, percent_col, '', subtotal_format)

        worksheet.set_column(0, percent_col, 16)