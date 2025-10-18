from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource


class InvoiceBillReport(models.AbstractModel):
    _name = 'report.inventory_report.inventory_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('product_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')


        worksheet = workbook.add_worksheet('Inventory Report')
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
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})

        logo_path = get_module_resource('inventory_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 4, logo_path, {
                'x_scale': .92,
                'y_scale': 0.190,
            })

        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col + 2, row + 4, col + 3, "")

        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Inventory Report", header_format0)
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
        worksheet.write(row, col, "Product Category", header_format)
        worksheet.write(row, col + 1, "Code", header_format)
        worksheet.write(row, col + 2, "Product", header_format)
        worksheet.write(row, col + 3, "Lot", header_format)
        worksheet.write(row, col + 4, "Expiry Date", header_format)
        worksheet.write(row, col + 5, "QTY", header_format)
        worksheet.write(row, col + 6, "Total Dos", header_format)
        worksheet.write(row, col + 7, "QTY Last 6M", header_format)
        worksheet.write(row, col + 8, "QTY Avg", header_format)
        worksheet.write(row, col + 9, "Equ/Month", header_format)
        worksheet.write(row, col + 10, "NAAP", header_format)
        worksheet.write(row, col + 11, "Value", header_format)
        row += 1

        # ---------------- Data Rows ----------------
        last_category = None
        category_totals = {
            'Total QTY': 0,
            'Total QTY Last 6M': 0,
            'Total QTY Avg': 0,
            'Total Equ/Month': 0,
            'Total NAAP': 0,
            'Total Value': 0,
            'Total_dos': 0,

        }

        for record in lots_data:
            # لو الكاتيجوري اتغيرت -> اطبع Total للأخيرة وابدأ الجديدة
            if last_category and record['Product Category'] != last_category:
                # Subtotal Row
                worksheet.write(row, col + 1, "Total", header_format)
                worksheet.write(row, col + 2, "", header_format)
                worksheet.write(row, col + 3, "", header_format)
                worksheet.write(row, col + 4, "", header_format)
                worksheet.write_number(row, col + 5, category_totals['Total QTY'], header_format)
                worksheet.write_number(row, col + 6, category_totals['Total_dos'], header_format)
                worksheet.write_number(row, col + 7, category_totals['Total QTY Last 6M'], header_format)
                worksheet.write_number(row, col + 8, category_totals['Total QTY Avg'], header_format)
                worksheet.write_number(row, col + 9, category_totals['Total Equ/Month'], header_format)
                worksheet.write_number(row, col + 10, category_totals['Total NAAP'], header_format)
                worksheet.write_number(row, col + 11, category_totals['Total Value'], header_format)
                row += 2  # نسيب سطر فاصل بعد الـ Subtotal

                # Reset totals
                category_totals = {k: 0 for k in category_totals}

            # لو كاتيجوري جديدة نطبعها في صف كامل لوحدها
            if record['Product Category'] != last_category:
                worksheet.merge_range(row, col, row, col + 11, record['Product Category'], header_format)
                last_category = record['Product Category']
                row += 1  # ننزل سطر بعد الكاتيجوري

            # كتابة بيانات المنتج
            worksheet.write(row, col + 1, record['Default Code'] or '', cell_format)
            worksheet.write(row, col + 2, record['Product'] or '', cell_format)
            worksheet.write(row, col + 3, record['Lots'] or '', cell_format)
            worksheet.write(row, col + 4, record['expiry_date'] or '', cell_format)
            worksheet.write_number(row, col + 5, record['on_hand_qty'], cell_format)
            worksheet.write_number(row, col + 6, record['Total Dos'], cell_format)
            worksheet.write_number(row, col + 7, record['sold_last_6_months'], cell_format)
            worksheet.write_number(row, col + 8, record['avg_sold_last_6_months'], cell_format)
            worksheet.write_number(row, col + 9, record['equ_month'], cell_format)
            worksheet.write_number(row, col + 10, record['naap'], cell_format)
            worksheet.write_number(row, col + 11, record['value'], cell_format)

            # نجمع القيم عشان subtotal
            category_totals['Total QTY'] += record['on_hand_qty']
            category_totals['Total QTY Last 6M'] += record['sold_last_6_months']
            category_totals['Total QTY Avg'] += record['avg_sold_last_6_months']
            category_totals['Total Equ/Month'] += record['equ_month']
            category_totals['Total NAAP'] += record['naap']
            category_totals['Total Value'] += record['value']
            category_totals['Total_dos'] += record['Total Dos']

            row += 1

        # بعد آخر كاتيجوري لازم نطبع subtotal
        if last_category:
            worksheet.write(row, col + 1, "Total", header_format)
            worksheet.write(row, col + 2, "", header_format)
            worksheet.write(row, col + 3, "", header_format)
            worksheet.write(row, col + 4, "", header_format)

            worksheet.write_number(row, col + 5, category_totals['Total QTY'], header_format)
            worksheet.write_number(row, col + 6, category_totals['Total_dos'], header_format)
            worksheet.write_number(row, col + 7, category_totals['Total QTY Last 6M'], header_format)
            worksheet.write_number(row, col + 8, category_totals['Total QTY Avg'], header_format)
            worksheet.write_number(row, col + 9, category_totals['Total Equ/Month'], header_format)
            worksheet.write_number(row, col + 10, category_totals['Total NAAP'], header_format)
            worksheet.write_number(row, col + 11, category_totals['Total Value'], header_format)
