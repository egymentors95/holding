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
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        worksheet = workbook.add_worksheet('Expense Report')
        row = 0
        col = 0

        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)

        # Formats
        header_format0 = workbook.add_format({'bold': True,
                                              'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format1 = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0',
                                             'align': 'left', 'valign': 'vcenter', 'border': 2})

        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})

        logo_path = get_module_resource('expense_product_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 6, logo_path, {
                'x_scale': .88,
                'y_scale': 0.190,
            })

        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col + 2, row + 4, col + 5, "")

        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Expense Report", header_format0)
        row += 1
        worksheet.write(row, col, f"Date from", header_format0)
        worksheet.write(row, col + 1, f"{date_from}", header_format0)
        row += 1
        worksheet.write(row, col, f"Date to", header_format0)
        worksheet.write(row, col + 1, f"{date_to}", header_format0)
        row += 1
        worksheet.write(row, col, f"Currency", header_format0)
        worksheet.write(row, col + 1, f"SR or USD", header_format0)
        row += 2

        # ---------------- Table Headers ----------------
        worksheet.write(row, col, "Team", header_format)
        worksheet.write(row, col + 1, "Accounts", header_format)

        employees = sorted(set([rec['employee'] for rec in lots_data if rec.get('employee')]))
        emp_col_map = {}
        for idx, emp in enumerate(employees):
            worksheet.write(row, col + 2 + idx, emp, header_format)
            emp_col_map[emp] = col + 2 + idx

        total_col = col + 2 + len(employees)
        worksheet.write(row, total_col, "Total", header_format)
        row += 1

        # ---------------- Fill Data + Subtotal per Team ----------------
        grand_totals = {emp: 0.0 for emp in employees}
        grand_totals["row_total"] = 0.0

        team_totals = {emp: 0.0 for emp in employees}
        team_totals["row_total"] = 0.0

        last_team = None  # لمتابعة آخر Team مكتوب

        for rec in lots_data:
            team = rec.get('sales_team')
            account = rec.get('account')
            debit = rec.get('debit') or 0.0
            employee = rec.get('employee')

            # لو التيم اتغير -> اطبع Subtotal للتيم السابق
            if last_team and team != last_team:
                worksheet.write(row, col, f"Subtotal {last_team}", header_format)
                worksheet.write(row, col + 1, "", header_format)
                for emp in employees:
                    worksheet.write_number(row, emp_col_map[emp], team_totals[emp], header_format)
                worksheet.write_number(row, total_col, team_totals["row_total"], header_format)
                row += 1

                # إعادة تعيين قيم التيم الجديدة
                team_totals = {emp: 0.0 for emp in employees}
                team_totals["row_total"] = 0.0

            # لو التيم جديد، اطبع اسمه في صف كامل
            if team != last_team:
                worksheet.merge_range(row, col, row, total_col, team or '', header_format1)
                last_team = team
                row += 1

            # كتابة البيانات
            worksheet.write(row, col, "", cell_format)  # Team فاضية لأنه مكتوب أعلاه
            worksheet.write(row, col + 1, account or '', cell_format)

            row_total = 0.0
            for emp in employees:
                value = debit if emp == employee else 0.0
                worksheet.write_number(row, emp_col_map[emp], value, cell_format)
                team_totals[emp] += value
                grand_totals[emp] += value
                row_total += value

            worksheet.write_number(row, total_col, row_total, cell_format)
            team_totals["row_total"] += row_total
            grand_totals["row_total"] += row_total

            row += 1

        # بعد آخر Team اطبع Subtotal
        if last_team:
            worksheet.write(row, col, f"Subtotal {last_team}", header_format)
            worksheet.write(row, col + 1, "", header_format)
            for emp in employees:
                worksheet.write_number(row, emp_col_map[emp], team_totals[emp], header_format)
            worksheet.write_number(row, total_col, team_totals["row_total"], header_format)
            row += 1

        # ---------------- Grand Total Row ----------------
        worksheet.write(row, col, "Grand Total", header_format)
        worksheet.write(row, col + 1, "", header_format)
        for emp in employees:
            worksheet.write_number(row, emp_col_map[emp], grand_totals[emp], header_format)
        worksheet.write_number(row, total_col, grand_totals["row_total"], header_format)