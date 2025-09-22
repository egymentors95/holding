from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource


class InvoiceBillReport(models.AbstractModel):
    _name = 'report.bill_product_report.purchase_bill_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('product_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        # if date_from:
        #     date_from_last_year = datetime.strptime(date_from, "%Y-%m-%d").replace(
        #         year=datetime.strptime(date_from, "%Y-%m-%d").year - 1)
        # else:
        #     date_from_last_year = None
        # if date_to:
        #     date_to_last_year = datetime.strptime(date_to, "%Y-%m-%d").replace(
        #         year=datetime.strptime(date_to, "%Y-%m-%d").year - 1)
        # else:
        #     date_to_last_year = None

        worksheet = workbook.add_worksheet('Purchase Report')
        row = 0
        col = 0

        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 17)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 27)
        worksheet.set_column('J:J', 15)

        # Formats
        header_format0 = workbook.add_format({'bold': True,
                                             'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format2 = workbook.add_format({'bold': True, 'bg_color': '#27C2F5',
                                              'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format3 = workbook.add_format({'bold': True, 'bg_color': '#27F5C1',
                                              'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format4 = workbook.add_format({'bold': True, 'bg_color': '#E6376F',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})

        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1,  'bottom': 1})

        logo_path = get_module_resource('bill_product_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 7, logo_path, {
                'x_scale': .92,
                'y_scale': 0.190,
            })

        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col+2, row+4, col+6, "")


        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Purchase Report", header_format0)
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
        worksheet.merge_range(row, col, row+1, col, "Product Category", header_format)
        worksheet.merge_range(row, col + 1, row+1, col + 1, "Default Code", header_format)
        worksheet.merge_range(row, col + 2, row+1, col + 2, "Product", header_format)

        # هيدر السنة اللي فاتت
        worksheet.merge_range(
            row, col + 3, row, col + 6,
            f"QTY",
            header_format2
        )

        # الهيدر الفرعي للسنة اللي فاتت
        worksheet.write(row + 1, col + 3, "Main Qty", header_format2)
        worksheet.write(row + 1, col + 4, "Foc", header_format2)
        worksheet.write(row + 1, col + 5, "Value", header_format2)
        worksheet.write(row + 1, col + 6, "NAAP", header_format2)


        # الهيدر الفرعي للفترة الحالية
        worksheet.merge_range(
            row, col + 7, row, col + 10,
            f"Full Year Plan",
            header_format3
        )
        worksheet.write(row + 1, col + 7, "Vendor", header_format3)
        worksheet.write(row + 1, col + 8, "QTY", header_format3)
        worksheet.write(row + 1, col + 9, "Value", header_format3)
        worksheet.write(row + 1, col + 10, "Ach.%", header_format3)
        row += 2

        # ---------------- Data Rows ----------------
        last_category = None
        category_totals = {
            'Total Quantity': 0,
            'Foc': 0,
            'Total Price': 0,
            'Nsap': 0,
            'Plan Quantity': 0,
            'Plan Value': 0,
            'Achive': 0,
        }

        for record in lots_data:
            # لو الكاتيجوري اتغيرت -> اطبع Total للأخيرة وابدأ الجديدة
            if last_category and record['Product Category'] != last_category:
                # Subtotal Row
                worksheet.write(row, col + 1, "Total", header_format)
                worksheet.write(row, col + 2, "", header_format)
                worksheet.write_number(row, col + 3, category_totals['Total Quantity'], header_format)
                worksheet.write_number(row, col + 4, category_totals['Foc'], header_format)
                worksheet.write_number(row, col + 5, category_totals['Total Price'], header_format)
                worksheet.write_number(row, col + 6, category_totals['Nsap'], header_format)
                worksheet.write(row, col + 7, "", header_format)
                worksheet.write_number(row, col + 8, category_totals['Plan Quantity'], header_format)
                worksheet.write_number(row, col + 9, category_totals['Plan Value'], header_format)
                worksheet.write_number(row, col + 10, category_totals['Achive'], header_format)
                row += 2  # نسيب سطر فاصل بعد الـ Subtotal

                # Reset totals
                category_totals = {k: 0 for k in category_totals}

            # لو كاتيجوري جديدة نطبعها في صف كامل لوحدها
            if record['Product Category'] != last_category:
                worksheet.merge_range(row, col, row, col + 10, record['Product Category'], header_format)
                last_category = record['Product Category']
                row += 1  # ننزل سطر بعد الكاتيجوري

            # كتابة بيانات المنتج
            worksheet.write(row, col + 1, record['Default Code'] or '', cell_format)
            worksheet.write(row, col + 2, record['Product'] or '', cell_format)
            worksheet.write_number(row, col + 3, record['Total Quantity'], cell_format)
            worksheet.write_number(row, col + 4, record['Foc'], cell_format)
            worksheet.write_number(row, col + 5, record['Total Price'], cell_format)
            worksheet.write_number(row, col + 6, record['Nsap'], cell_format)
            worksheet.write(row, col + 7, record['Vendor'], cell_format)
            worksheet.write_number(row, col + 8, record['Plan Quantity'], cell_format)
            worksheet.write_number(row, col + 9, record['Plan Value'], cell_format)
            worksheet.write_number(row, col + 10, record['Achive'], cell_format)

            # نجمع القيم عشان subtotal
            category_totals['Total Quantity'] += record['Total Quantity']
            category_totals['Foc'] += record['Foc']
            category_totals['Total Price'] += record['Total Price']
            category_totals['Nsap'] += record['Nsap']
            category_totals['Plan Quantity'] += record['Plan Quantity']
            category_totals['Plan Value'] += record['Plan Value']
            category_totals['Achive'] += record['Achive']

            row += 1

        # بعد آخر كاتيجوري لازم نطبع subtotal
        if last_category:
            worksheet.write(row, col + 1, "Total", header_format)
            worksheet.write(row, col + 2, "", header_format)

            worksheet.write_number(row, col + 3, category_totals['Total Quantity'], header_format)
            worksheet.write_number(row, col + 4, category_totals['Foc'], header_format)
            worksheet.write_number(row, col + 5, category_totals['Total Price'], header_format)
            worksheet.write_number(row, col + 6, category_totals['Nsap'], header_format)
            worksheet.write(row, col + 7, "", header_format)

            worksheet.write_number(row, col + 8, category_totals['Plan Quantity'], header_format)
            worksheet.write_number(row, col + 9, category_totals['Plan Value'], header_format)
            worksheet.write_number(row, col + 10, category_totals['Achive'], header_format)

