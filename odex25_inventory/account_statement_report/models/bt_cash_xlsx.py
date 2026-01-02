from odoo import models
from datetime import datetime


class BtCashXlsxReport(models.AbstractModel):
    _name = 'report.account_statement_report.bt_cash_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'BT Cash Statement XLSX'

    def generate_xlsx_report(self, workbook, data, records):
        wizard = records[0]
        report_data = wizard.get_report_data()
        lines = report_data['lines']

        worksheet = workbook.add_worksheet('BT Cash Statement')

        # =====================
        # Formats
        # =====================
        header = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'bg_color': '#E7E6E6'
        })
        cell = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_number = workbook.add_format({
            'border': 1, 'align': 'right', 'valign': 'vcenter',
            'num_format': '#,##0.00'
        })
        title = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center'
        })

        # =====================
        # Column width
        # =====================
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 18)

        row = 0
        col = 0

        # =====================
        # Header info
        # =====================
        worksheet.merge_range(row, col, row, col + 4, 'كشف حساب BT Cash', title)
        row += 2

        worksheet.write(row, col, 'العميل', header)
        worksheet.merge_range(row, col + 1, row, col + 4, report_data['partner_name'], cell)
        row += 1

        worksheet.write(row, col, 'من', header)
        worksheet.write(row, col + 1, str(report_data['date_from']), cell)
        worksheet.write(row, col + 2, 'إلى', header)
        worksheet.write(row, col + 3, str(report_data['date_to']), cell)
        row += 2

        # =====================
        # Table Header
        # =====================
        worksheet.write_row(row, col, [
            'التاريخ',
            'نوع الحركة',
            'مدين (وارد)',
            'دائن (منصرف)',
            'الرصيد'
        ], header)
        row += 1

        # =====================
        # Data rows
        # =====================
        for line in lines:
            worksheet.write(row, col, str(line['date']), cell)
            worksheet.write(row, col + 1, line['move_type'], cell)
            worksheet.write_number(row, col + 2, line['debit'], cell_number)
            worksheet.write_number(row, col + 3, line['credit'], cell_number)
            worksheet.write_number(row, col + 4, line['balance'], cell_number)
            row += 1
