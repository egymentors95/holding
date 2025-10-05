from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource
from itertools import groupby


class ProfitReport(models.AbstractModel):
    _name = 'report.profit_report.profit_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('report_data', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from:
            date_from_last_year = datetime.strptime(date_from, "%Y-%m-%d").replace(year=datetime.strptime(date_from, "%Y-%m-%d").year - 1)
        else:
            date_from_last_year = None
        if date_to:
            date_to_last_year = datetime.strptime(date_to, "%Y-%m-%d").replace(year=datetime.strptime(date_to, "%Y-%m-%d").year - 1)
        else:
            date_to_last_year = None

        worksheet = workbook.add_worksheet('Profit Report')
        row = 0
        col = 0

        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 12)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('O:O', 15)


        # Formats
        header_format0 = workbook.add_format({'bold': True,
                                             'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format2 = workbook.add_format({'bold': True, 'bg_color': '#27C2F5',
                                              'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format3 = workbook.add_format({'bold': True, 'bg_color': '#27F5C1',
                                              'align': 'center', 'valign': 'vcenter', 'border': 2})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})
        cell_format_light = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 1, 'right': 1, 'top': 1, 'bottom': 1})
        cell_format_light_right = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                 'border': 0, 'left': 1, 'right': 2, 'top': 1, 'bottom': 1})


        logo_path = get_module_resource('profit_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 9, logo_path, {
                'x_scale': .88,
                'y_scale': 0.190,
            })


        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col + 2, row + 4, col + 8, "")

        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Profit Report", header_format0)
        row += 1
        worksheet.write(row, col, f"Date from", header_format0)
        worksheet.write(row, col + 1, f"{date_from}", header_format0)
        row += 1
        worksheet.write(row, col, f"Date to", header_format0)
        worksheet.write(row, col + 1, f"{date_to}", header_format0)
        row += 1
        worksheet.write(row, col, f"Currency", header_format0)
        worksheet.write(row, col + 1, f"SR", header_format0)
        row += 2

        # تأكد إن البيانات متسلسلة حسب اسم البارتنر قبل الـ groupby
        lots_data.sort(key=lambda r: r.get('Partner') or '')

        all_records = []  # for grand total

        for partner_name, partner_records in groupby(lots_data, key=lambda r: r.get('Partner') or 'Unknown Partner'):
            partner_records = list(partner_records)
            all_records += partner_records

            # Partner title
            worksheet.merge_range(row, col, row, col + 14, f"Partner: {partner_name}", header_format0)
            row += 2

            # Table headers
            worksheet.merge_range(row, col, row + 1, col, "Product Category", header_format)
            worksheet.merge_range(row, col + 1, row + 1, col + 1, "Default Code", header_format)
            worksheet.merge_range(row, col + 2, row + 1, col + 2, "Product", header_format)

            worksheet.merge_range(row, col + 3, row, col + 8,
                                  f"Last Year ({date_from_last_year.date()} → {date_to_last_year.date()})",
                                  header_format2)
            worksheet.write(row + 1, col + 3, "Total QTY", header_format2)
            worksheet.write(row + 1, col + 4, "Total Value", header_format2)
            worksheet.write(row + 1, col + 5, "NASP", header_format2)
            worksheet.write(row + 1, col + 6, "NAPP", header_format2)
            worksheet.write(row + 1, col + 7, "Profit Value", header_format2)
            worksheet.write(row + 1, col + 8, "Profit Margin", header_format2)

            worksheet.merge_range(row, col + 9, row, col + 14,
                                  f"Current Period ({date_from} → {date_to})",
                                  header_format3)
            worksheet.write(row + 1, col + 9, "Total QTY", header_format3)
            worksheet.write(row + 1, col + 10, "Total Value", header_format3)
            worksheet.write(row + 1, col + 11, "NASP", header_format3)
            worksheet.write(row + 1, col + 12, "NAPP", header_format3)
            worksheet.write(row + 1, col + 13, "Profit Value", header_format3)
            worksheet.write(row + 1, col + 14, "Profit Margin", header_format3)
            row += 2

            # Data rows
            last_category = None
            for record in partner_records:
                if record['Product Category'] == last_category:
                    worksheet.write(row, col, "", cell_format)
                else:
                    worksheet.write(row, col, record['Product Category'], cell_format)
                    last_category = record['Product Category']

                worksheet.write(row, col + 1, record['Default Code'] or '', cell_format)
                worksheet.write(row, col + 2, record['Product'] or '', cell_format)
                worksheet.write_number(row, col + 3, round(record['Last Year Total Quantity'], 2), cell_format_light)
                worksheet.write_number(row, col + 4, round(record['Last Year Total Price'], 2), cell_format_light)
                worksheet.write_number(row, col + 5, round(record['Last Year Nsap'], 2), cell_format_light)
                worksheet.write_number(row, col + 6, round(record['Last Year Naap'], 2), cell_format_light)
                worksheet.write_number(row, col + 7, round(record['Last Profit Value'], 2), cell_format_light)
                worksheet.write_number(row, col + 8, round(record['Last Margin'], 2), cell_format_light)
                worksheet.write_number(row, col + 9, round(record['Total Quantity'], 2), cell_format_light)
                worksheet.write_number(row, col + 10, round(record['Total Price'], 2), cell_format_light)
                worksheet.write_number(row, col + 11, round(record['Nsap'], 2), cell_format_light)
                worksheet.write_number(row, col + 12, round(record['Naap'], 2), cell_format_light)
                worksheet.write_number(row, col + 13, round(record['Profit Value'], 2), cell_format_light)
                worksheet.write_number(row, col + 14, round(record['Margin'], 2), cell_format_light)
                row += 1

            # Partner subtotal
            total_last_qty = sum(r['Last Year Total Quantity'] for r in partner_records)
            total_last_value = sum(r['Last Year Total Price'] for r in partner_records)
            total_last_profit = sum(r['Last Profit Value'] for r in partner_records)
            total_curr_qty = sum(r['Total Quantity'] for r in partner_records)
            total_curr_value = sum(r['Total Price'] for r in partner_records)
            total_curr_profit = sum(r['Profit Value'] for r in partner_records)
            total_last_margin = (total_last_profit / total_last_value * 100) if total_last_value else 0
            total_curr_margin = (total_curr_profit / total_curr_value * 100) if total_curr_value else 0

            worksheet.write(row, col, "Total", cell_format)
            worksheet.write_blank(row, col + 1, None, cell_format)
            worksheet.write_blank(row, col + 2, None, cell_format)
            worksheet.write_number(row, col + 3, total_last_qty, cell_format)
            worksheet.write_number(row, col + 4, total_last_value, cell_format)
            worksheet.write_blank(row, col + 5, None, cell_format)
            worksheet.write_blank(row, col + 6, None, cell_format)
            worksheet.write_number(row, col + 7, total_last_profit, cell_format)
            worksheet.write_number(row, col + 8, total_last_margin, cell_format)
            worksheet.write_number(row, col + 9, total_curr_qty, cell_format)
            worksheet.write_number(row, col + 10, total_curr_value, cell_format)
            worksheet.write_blank(row, col + 11, None, cell_format)
            worksheet.write_blank(row, col + 12, None, cell_format)
            worksheet.write_number(row, col + 13, total_curr_profit, cell_format)
            worksheet.write_number(row, col + 14, total_curr_margin, cell_format)

            row += 3  # space after each partner

        # Grand total (all data)
        if all_records:
            grand_last_qty = sum(r['Last Year Total Quantity'] for r in all_records)
            grand_last_value = sum(r['Last Year Total Price'] for r in all_records)
            grand_last_profit = sum(r['Last Profit Value'] for r in all_records)
            grand_curr_qty = sum(r['Total Quantity'] for r in all_records)
            grand_curr_value = sum(r['Total Price'] for r in all_records)
            grand_curr_profit = sum(r['Profit Value'] for r in all_records)
            grand_last_margin = (grand_last_profit / grand_last_value * 100) if grand_last_value else 0
            grand_curr_margin = (grand_curr_profit / grand_curr_value * 100) if grand_curr_value else 0

            worksheet.merge_range(row, col, row, col + 2, "GRAND TOTAL", cell_format)
            worksheet.write_number(row, col + 3, grand_last_qty, cell_format)
            worksheet.write_number(row, col + 4, grand_last_value, cell_format)
            worksheet.write_blank(row, col + 5, None, cell_format)
            worksheet.write_blank(row, col + 6, None, cell_format)
            worksheet.write_number(row, col + 7, grand_last_profit, cell_format)
            worksheet.write_number(row, col + 8, grand_last_margin, cell_format)
            worksheet.write_number(row, col + 9, grand_curr_qty, cell_format)
            worksheet.write_number(row, col + 10, grand_curr_value, cell_format)
            worksheet.write_blank(row, col + 11, None, cell_format)
            worksheet.write_blank(row, col + 12, None, cell_format)
            worksheet.write_number(row, col + 13, grand_curr_profit, cell_format)
            worksheet.write_number(row, col + 14, grand_curr_margin, cell_format)