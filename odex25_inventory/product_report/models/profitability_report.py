from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource


class ProfitabilityReport(models.AbstractModel):
    _name = 'report.product_report.profitability_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('product_ids', [])
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

        worksheet = workbook.add_worksheet('Sales Report')
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


        # Formats
        header_format0 = workbook.add_format({'bold': True,
                                              'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_format = workbook.add_format({'bold': True,
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})

        logo_path = get_module_resource('product_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 9, logo_path, {
                'x_scale': .88,
                'y_scale': 0.190,
            })


        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col + 2, row + 4, col + 8, "")

        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Sales Report", header_format0)
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
            row, col + 3, row, col + 5,
            f"Last ({date_from_last_year.date()} → {date_to_last_year.date()})",
            header_format
        )

        # الهيدر الفرعي للسنة اللي فاتت
        worksheet.write(row + 1, col + 3, "Quantity", header_format)
        worksheet.write(row + 1, col + 4, "Price", header_format)
        worksheet.write(row + 1, col + 5, "Nasp", header_format)

        # هيدر الفترة الحالية
        worksheet.merge_range(
            row, col + 6, row, col + 9,
            f"Current ({date_from} → {date_to})",
            header_format
        )

        # الهيدر الفرعي للفترة الحالية
        worksheet.write(row + 1, col + 6, "Total Quantity", header_format)
        worksheet.write(row + 1, col + 7, "Total Price", header_format)
        worksheet.write(row + 1, col + 8, "Nasp", header_format)
        worksheet.write(row + 1, col + 9, "Sales Person", header_format)

        worksheet.merge_range(
            row, col + 10, row, col + 12,
            f"YTD Plan ({date_from} → {date_to})",
            header_format
        )
        worksheet.write(row + 1, col + 10, "Plan Quantity", header_format)
        worksheet.write(row + 1, col + 11, "Value", header_format)
        worksheet.write(row + 1, col + 12, "Nasp", header_format)
        worksheet.merge_range(row, col + 13, row+1, col + 13, "Qty %", header_format)
        worksheet.merge_range(row, col + 14, row+1, col + 14, "Value %", header_format)

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

            worksheet.write_number(row, col + 3, record['Last Year Total Quantity'], cell_format)
            worksheet.write_number(row, col + 4, record['Last Year Total Price'], cell_format)
            worksheet.write_number(row, col + 5, record['Last Year Nsap'], cell_format)


            worksheet.write_number(row, col + 6, record['Total Quantity'], cell_format)
            worksheet.write_number(row, col + 7, record['Total Price'], cell_format)
            worksheet.write_number(row, col + 8, round(record['Nsap'],2), cell_format)
            worksheet.write(row, col + 9, record['Sales Person'], cell_format)

            worksheet.write_number(row, col + 10, record['Total Plan Quantity'], cell_format)
            worksheet.write_number(row, col + 11, record['Total Plan Price'], cell_format)
            worksheet.write_number(row, col + 12, record['Plan Nsap'], cell_format)
            worksheet.write_number(row, col + 13, record['QTY'], cell_format)
            worksheet.write_number(row, col + 14, record['Value'], cell_format)


            row += 1
