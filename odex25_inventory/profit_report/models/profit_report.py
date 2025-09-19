from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource


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

        # ---------------- Table Headers ----------------
        worksheet.merge_range(row, col, row+1, col, "Product Category", header_format)
        worksheet.merge_range(row, col + 1, row+1, col + 1, "Default Code", header_format)
        worksheet.merge_range(row, col + 2, row+1, col + 2, "Product", header_format)

        # هيدر السنة اللي فاتت
        worksheet.merge_range(
            row, col + 3, row, col + 8,
            f"Last Year ({date_from_last_year.date()} → {date_to_last_year.date()})",
            header_format2
        )

        # الهيدر الفرعي للسنة اللي فاتت
        worksheet.write(row + 1, col + 3, "Total Quantity", header_format2)
        worksheet.write(row + 1, col + 4, "Total Price", header_format2)
        worksheet.write(row + 1, col + 5, "NASP", header_format2)
        worksheet.write(row + 1, col + 6, "NAPP", header_format2)
        worksheet.write(row + 1, col + 7, "Profit Value", header_format2)
        worksheet.write(row + 1, col + 8, "Profit Margin", header_format2)

        # هيدر الفترة الحالية
        worksheet.merge_range(
            row, col + 9, row, col + 14,
            f"Current Period ({date_from} → {date_to})",
            header_format3
        )

        # الهيدر الفرعي للفترة الحالية
        worksheet.write(row + 1, col + 9, "Total Quantity", header_format3)
        worksheet.write(row + 1, col + 10, "Total Price", header_format3)
        worksheet.write(row + 1, col + 11, "NASP", header_format3)
        worksheet.write(row + 1, col + 12, "NAPP", header_format3)
        worksheet.write(row + 1, col + 13, "Profit Value", header_format3)
        worksheet.write(row + 1, col + 14, "Profit Margin", header_format3)

        row += 2

        # ---------------- Data Rows ----------------
        last_category = None
        for record in lots_data:
            # Product Category (merge if same)
            if record['Product Category'] == last_category:
                worksheet.write(row, col, "", cell_format)
            else:
                worksheet.write(row, col, record['Product Category'], cell_format)
                last_category = record['Product Category']

            worksheet.write(row, col + 1, record['Default Code'] or '', cell_format)
            worksheet.write(row, col + 2, record['Product'] or '', cell_format)

            worksheet.write_number(row, col + 3, record['Last Year Total Quantity'], cell_format_light)
            worksheet.write_number(row, col + 4, record['Last Year Total Price'], cell_format_light)
            worksheet.write_number(row, col + 5, record['Last Year Nsap'], cell_format_light)
            worksheet.write_number(row, col + 6, record['Last Year Naap'], cell_format_light)
            worksheet.write_number(row, col + 7, record['Last Profit Value'], cell_format_light)
            worksheet.write_number(row, col + 8, record['Last Margin'], cell_format_light_right)


            worksheet.write_number(row, col + 9, record['Total Quantity'], cell_format_light)
            worksheet.write_number(row, col + 10, record['Total Price'], cell_format_light)
            worksheet.write_number(row, col + 11, round(record['Nsap'],2), cell_format_light)
            worksheet.write_number(row, col + 12, round(record['Naap'],2), cell_format_light)
            worksheet.write_number(row, col + 13, record['Profit Value'], cell_format_light)
            worksheet.write_number(row, col + 14, round(record['Margin'],2), cell_format_light_right)

            row += 1
