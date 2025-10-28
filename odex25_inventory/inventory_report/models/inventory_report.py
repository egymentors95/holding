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
        header_format = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0', 'num_format': '#,##0.00',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})

        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': '#,##0.00',
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
        last_private_category = None

        category_totals = {
            'Total QTY': 0,
            'Total QTY Last 6M': 0,
            'Total QTY Avg': 0,
            'Total Equ/Month': 0,
            'Total NAAP': 0,
            'Total Value': 0,
            'Total_dos': 0,
        }

        private_totals = {k: 0 for k in category_totals}

        for record in lots_data:
            product_cat = record.get('Product Category') or 'Other Category'
            private_cat = record.get('private_category') or 'Other Products'

            # --- لو Product Category اتغيرت ---
            if last_category and product_cat != last_category:
                # Subtotal لآخر Private Category
                worksheet.merge_range(row, col + 1, row, col+4, "Subtotal", header_format)
                worksheet.write_number(row, col + 5, private_totals['Total QTY'], header_format)
                worksheet.write_number(row, col + 6, private_totals['Total_dos'] / 1000000, header_format)
                worksheet.write_number(row, col + 7, private_totals['Total QTY Last 6M'], header_format)
                worksheet.write_number(row, col + 8, private_totals['Total QTY Avg'], header_format)
                worksheet.write_number(row, col + 9, private_totals['Total Equ/Month'], header_format)
                worksheet.write_number(row, col + 10, private_totals['Total NAAP'], header_format)
                worksheet.write_number(row, col + 11, private_totals['Total Value'], header_format)
                row += 2

                # Subtotal للـ Product Category كله
                worksheet.merge_range(row, col + 1, row, col+4, f"Total ({last_category})", header_format)
                worksheet.write_number(row, col + 5, category_totals['Total QTY'], header_format)
                worksheet.write_number(row, col + 6, category_totals['Total_dos'] / 1000000, header_format)
                worksheet.write_number(row, col + 7, category_totals['Total QTY Last 6M'], header_format)
                worksheet.write_number(row, col + 8, category_totals['Total QTY Avg'], header_format)
                worksheet.write_number(row, col + 9, category_totals['Total Equ/Month'], header_format)
                worksheet.write_number(row, col + 10, category_totals['Total NAAP'], header_format)
                worksheet.write_number(row, col + 11, category_totals['Total Value'], header_format)
                row += 3

                # Reset totals
                category_totals = {k: 0 for k in category_totals}
                private_totals = {k: 0 for k in private_totals}

                worksheet.merge_range(row, col, row, col + 11, product_cat, header_format)
                row += 1
                last_private_category = None
                last_category = product_cat

            # --- لو Private Category اتغيرت ---
            if last_private_category and private_cat != last_private_category:
                worksheet.merge_range(row, col + 1, row, col+4, "Subtotal", header_format)
                worksheet.write_number(row, col + 5, private_totals['Total QTY'], header_format)
                worksheet.write_number(row, col + 6, private_totals['Total_dos'] / 1000000, header_format)
                worksheet.write_number(row, col + 7, private_totals['Total QTY Last 6M'], header_format)
                worksheet.write_number(row, col + 8, private_totals['Total QTY Avg'], header_format)
                worksheet.write_number(row, col + 9, private_totals['Total Equ/Month'], header_format)
                worksheet.write_number(row, col + 10, private_totals['Total NAAP'], header_format)
                worksheet.write_number(row, col + 11, private_totals['Total Value'], header_format)
                row += 2

                private_totals = {k: 0 for k in private_totals}

            # --- لو Product Category جديدة ---
            if product_cat != last_category:
                worksheet.merge_range(row, col, row, col + 11, product_cat, header_format)
                last_category = product_cat
                last_private_category = None
                row += 1

            # --- كتابة بيانات المنتج ---
            worksheet.write(row, col + 1, record.get('Default Code') or '', cell_format)
            worksheet.write(row, col + 2, record.get('Product') or '', cell_format)
            worksheet.write(row, col + 3, record.get('Lots') or '', cell_format)
            worksheet.write(row, col + 4, record.get('expiry_date') or '', cell_format)
            worksheet.write_number(row, col + 5, record.get('on_hand_qty', 0), cell_format)
            worksheet.write_number(row, col + 6, record.get('Total Dos', 0), cell_format)
            worksheet.write_number(row, col + 7, record.get('sold_last_6_months', 0), cell_format)
            worksheet.write_number(row, col + 8, record.get('avg_sold_last_6_months', 0), cell_format)
            worksheet.write_number(row, col + 9, record.get('equ_month', 0), cell_format)
            worksheet.write_number(row, col + 10, record.get('naap', 0), cell_format)
            worksheet.write_number(row, col + 11, record.get('value', 0), cell_format)

            # --- تجميع القيم ---
            for totals_dict in (category_totals, private_totals):
                totals_dict['Total QTY'] += record.get('on_hand_qty', 0)
                totals_dict['Total_dos'] += record.get('Total Dos', 0)
                totals_dict['Total QTY Last 6M'] += record.get('sold_last_6_months', 0)
                totals_dict['Total QTY Avg'] += record.get('avg_sold_last_6_months', 0)
                totals_dict['Total Equ/Month'] += record.get('equ_month', 0)
                totals_dict['Total NAAP'] += record.get('naap', 0)
                totals_dict['Total Value'] += record.get('value', 0)

            last_private_category = private_cat
            row += 1

        # --- بعد آخر Private Category / Product Category ---
        if last_private_category:
            worksheet.merge_range(row, col + 1, row, col + 4, "Subtotal", header_format)
            worksheet.write_number(row, col + 5, private_totals['Total QTY'], header_format)
            worksheet.write_number(row, col + 6, private_totals['Total_dos'] / 1000000, header_format)
            worksheet.write_number(row, col + 7, private_totals['Total QTY Last 6M'], header_format)
            worksheet.write_number(row, col + 8, private_totals['Total QTY Avg'], header_format)
            worksheet.write_number(row, col + 9, private_totals['Total Equ/Month'], header_format)
            worksheet.write_number(row, col + 10, private_totals['Total NAAP'], header_format)
            worksheet.write_number(row, col + 11, private_totals['Total Value'], header_format)
            row += 2

        if last_category:
            worksheet.merge_range(row, col + 1, row, col + 4, f"Total ({last_category})", header_format)
            worksheet.write_number(row, col + 5, category_totals['Total QTY'], header_format)
            worksheet.write_number(row, col + 6, category_totals['Total_dos'] / 1000000, header_format)
            worksheet.write_number(row, col + 7, category_totals['Total QTY Last 6M'], header_format)
            worksheet.write_number(row, col + 8, category_totals['Total QTY Avg'], header_format)
            worksheet.write_number(row, col + 9, category_totals['Total Equ/Month'], header_format)
            worksheet.write_number(row, col + 10, category_totals['Total NAAP'], header_format)
            worksheet.write_number(row, col + 11, category_totals['Total Value'], header_format)

