from odoo import models

class TaxReportXlsx(models.AbstractModel):
    _name = 'report.taxes_reports.total_tax_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Tax Summary')
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})


        sheet.set_column('A:A', 30)  # الوصف
        sheet.set_column('B:B', 20)  # المبلغ
        sheet.set_column('C:C', 20)  # التعديل
        sheet.set_column('D:D', 20)  # الضريبة


        sheet.write(0, 0, 'الوصف', bold)
        sheet.write(0, 1, 'المبلغ', bold)
        sheet.write(0, 2, 'التعديل', bold)
        sheet.write(0, 3, 'الضريبة', bold)

        row = 1
        sales_done = False  # عشان نعرف إمتى نضيف الفاصل

        for line in data.get('lines', []):
            # أول صف مشتريات: نضيف 3 صفوف فاضية قبلها
            if not sales_done and line['description'].startswith('المشتريات'):
                row += 3
                sales_done = True

            sheet.write(row, 0, line['description'])
            sheet.write_number(row, 1, line['price'], money)
            sheet.write_number(row, 2, line['refund'], money)
            sheet.write_number(row, 3, line['vat'], money)
            row += 1
