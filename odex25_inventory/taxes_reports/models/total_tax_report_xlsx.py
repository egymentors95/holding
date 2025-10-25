from odoo import models

class TaxReportXlsx(models.AbstractModel):
    _name = 'report.taxes_reports.total_tax_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('ملخص الضريبة')

        # ====== التنسيقات ======
        header = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#B7DEE8', 'border': 1
        })
        title = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#9BC2E6', 'border': 1
        })
        text = workbook.add_format({'align': 'right', 'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00', 'align': 'center', 'border': 1})

        # ====== ضبط عرض الأعمدة ======
        sheet.set_column('A:A', 55)
        sheet.set_column('B:D', 20)

        row = 0

        # ===================== جدول المبيعات =====================
        sheet.merge_range(row, 0, row, 3, 'جدول المبيعات', title)
        row += 1

        headers = ['الوصف', 'المبلغ', 'التعديل', 'الضريبة']
        for col, head in enumerate(headers):
            sheet.write(row, col, head, header)
        row += 1

        for line in data.get('lines', []):
            desc = line['description']
            if (
                    desc.startswith('المبيعات')
                    or desc in ['صادرات', 'مبيعات معفاة']
                    or 'الإجمالي (المبيعات)' in desc
            ):
                sheet.write(row, 0, desc, text)
                sheet.write_number(row, 1, line['price'], money)
                sheet.write_number(row, 2, line['refund'], money)
                sheet.write_number(row, 3, line['vat'], money)
                row += 1

        # فاصل بسيط بين الجدولين
        row += 2

        # ===================== جدول المشتريات =====================
        sheet.merge_range(row, 0, row, 3, 'جدول المشتريات', title)
        row += 1

        for col, head in enumerate(headers):
            sheet.write(row, col, head, header)
        row += 1

        for line in data.get('lines', []):
            desc = line['description']
            if (desc.startswith('المشتريات') or
                'الإستيرادات' in desc or
                'الإجمالي (المشتريات)' in desc):
                sheet.write(row, 0, desc, text)
                sheet.write_number(row, 1, line['price'], money)
                sheet.write_number(row, 2, line['refund'], money)
                sheet.write_number(row, 3, line['vat'], money)
                row += 1

        # فاصل واضح بين الجداول
        row += 3

        # ===================== جدول الضريبة النهائية =====================
        sheet.merge_range(row, 0, row, 3, 'ملخص الضريبة النهائية', title)
        row += 1

        sheet.write(row, 0, 'الوصف', header)
        sheet.write(row, 1, '', header)
        sheet.write(row, 2, '', header)
        sheet.write(row, 3, 'القيمة', header)
        row += 1

        for line in data.get('lines', []):
            desc = line['description']
            if desc in ['ضريبة المخرجات', 'ضريبة المدخلات', 'صافي الضريبة المستحقة']:
                sheet.write(row, 0, desc, text)
                sheet.write(row, 3, line['vat'], money)
                row += 1
