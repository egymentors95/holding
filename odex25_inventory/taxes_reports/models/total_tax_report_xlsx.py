from odoo import models

class TaxReportXlsx(models.AbstractModel):
    _name = 'report.taxes_reports.total_tax_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('ملخص الضريبة')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        text = workbook.add_format({'align': 'right', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00', 'align': 'center', 'border': 1})
        title = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9E1F2', 'border': 1})

        # ضبط عرض الأعمدة
        sheet.set_column('A:A', 55)
        sheet.set_column('B:D', 20)

        row = 0

        # ===================== جدول المبيعات =====================
        sheet.merge_range(row, 0, row, 3, 'جدول المبيعات', title)
        row += 1

        headers = ['الوصف', 'المبلغ', 'التعديل', 'الضريبة']
        for col, head in enumerate(headers):
            sheet.write(row, col, head, bold)
        row += 1

        for line in data.get('lines', []):
            if line['description'].startswith('المبيعات') or 'الإجمالي (المبيعات)' in line['description']:
                sheet.write(row, 0, line['description'], text)
                sheet.write_number(row, 1, line['price'], money)
                sheet.write_number(row, 2, line['refund'], money)
                sheet.write_number(row, 3, line['vat'], money)
                row += 1

        # فاصل صفين
        row += 2

        # ===================== جدول المشتريات =====================
        sheet.merge_range(row, 0, row, 3, 'جدول المشتريات', title)
        row += 1

        for col, head in enumerate(headers):
            sheet.write(row, col, head, bold)
        row += 1

        for line in data.get('lines', []):
            if line['description'].startswith('المشتريات') or 'الإستيرادات' in line['description'] or 'الإجمالي (المشتريات)' in line['description']:
                sheet.write(row, 0, line['description'], text)
                sheet.write_number(row, 1, line['price'], money)
                sheet.write_number(row, 2, line['refund'], money)
                sheet.write_number(row, 3, line['vat'], money)
                row += 1

        # فاصل صفين
        row += 2

        # ===================== جدول الضريبة النهائية =====================
        sheet.merge_range(row, 0, row, 3, 'ملخص الضريبة النهائية', title)
        row += 1

        sheet.write(row, 0, 'الوصف', bold)
        sheet.write(row, 1, '', bold)
        sheet.write(row, 2, '', bold)
        sheet.write(row, 3, 'القيمة', bold)
        row += 1

        for line in data.get('lines', []):
            if line['description'] in ['ضريبة المخرجات', 'ضريبة المدخلات', 'صافي الضريبة المستحقة']:
                sheet.write(row, 0, line['description'], text)
                sheet.write(row, 3, line['vat'], money)
                row += 1
