from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource
from collections import defaultdict


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

        # ---------------- Column Widths ----------------
        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 17)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 12)

        # ---------------- Formats ----------------
        header_format0 = workbook.add_format({'bold': True,
                                              'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0', 'num_format': '#,##0.00',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': '#,##0.00',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})

        # ---------------- Logo ----------------
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
        headers = ["Product Category", "Code", "Product", "Lot", "Expiry Date",
                   "QTY", "Total Dos", "QTY Last 6M", "QTY Avg", "Equ/Month", "NAAP", "Value"]
        for i, h in enumerate(headers):
            worksheet.write(row, col + i, h, header_format)
        row += 1

        # ---------------- Group Data ----------------
        grouped_data = defaultdict(lambda: defaultdict(list))
        for record in lots_data:
            product_cat = record.get('Product Category') or 'Other Category'
            private_cat = record.get('private_category') or 'Other Products'
            grouped_data[product_cat][private_cat].append(record)

        category_totals = {
            'Total QTY': 0,
            'Total QTY Last 6M': 0,
            'Total QTY Avg': 0,
            'Total Equ/Month': 0,
            'Total NAAP': 0,
            'Total Value': 0,
            'Total_dos': 0,
        }

        # ---------------- Write Data ----------------
        for product_cat, privates in grouped_data.items():
            worksheet.merge_range(row, col, row, col + 11, product_cat, header_format)
            row += 1

            product_cat_totals = {k: 0 for k in category_totals}

            for private_cat, records_list in privates.items():
                worksheet.merge_range(row, col + 1, row, col + 11, private_cat, header_format)
                row += 1

                private_totals = {k: 0 for k in category_totals}

                for record in records_list:
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

                    for totals_dict in (product_cat_totals, private_totals):
                        totals_dict['Total QTY'] += record.get('on_hand_qty', 0)
                        totals_dict['Total_dos'] += record.get('Total Dos', 0)
                        totals_dict['Total QTY Last 6M'] += record.get('sold_last_6_months', 0)
                        totals_dict['Total QTY Avg'] += record.get('avg_sold_last_6_months', 0)
                        totals_dict['Total Equ/Month'] += record.get('equ_month', 0)
                        totals_dict['Total NAAP'] += record.get('naap', 0)
                        totals_dict['Total Value'] += record.get('value', 0)
                    row += 1

                # Subtotal private category
                worksheet.merge_range(row, col + 1, row, col + 4, "Subtotal", header_format)
                worksheet.write_number(row, col + 5, private_totals['Total QTY'], header_format)
                worksheet.write_number(row, col + 6, private_totals['Total_dos'] / 1000000, header_format)
                worksheet.write_number(row, col + 7, private_totals['Total QTY Last 6M'], header_format)
                worksheet.write_number(row, col + 8, private_totals['Total QTY Avg'], header_format)
                worksheet.write_number(row, col + 9, private_totals['Total Equ/Month'], header_format)
                worksheet.write_number(row, col + 10, private_totals['Total NAAP'], header_format)
                worksheet.write_number(row, col + 11, private_totals['Total Value'], header_format)
                row += 2

            # Total for product category
            worksheet.merge_range(row, col + 1, row, col + 4, f"Total ({product_cat})", header_format)
            worksheet.write_number(row, col + 5, product_cat_totals['Total QTY'], header_format)
            worksheet.write_number(row, col + 6, product_cat_totals['Total_dos'] / 1000000, header_format)
            worksheet.write_number(row, col + 7, product_cat_totals['Total QTY Last 6M'], header_format)
            worksheet.write_number(row, col + 8, product_cat_totals['Total QTY Avg'], header_format)
            worksheet.write_number(row, col + 9, product_cat_totals['Total Equ/Month'], header_format)
            worksheet.write_number(row, col + 10, product_cat_totals['Total NAAP'], header_format)
            worksheet.write_number(row, col + 11, product_cat_totals['Total Value'], header_format)
            row += 3

