from odoo import models
from datetime import datetime
import xlsxwriter


class ProfitabilityReport(models.AbstractModel):
    _name = 'report.product_report.profitability_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        lots_data = data.get('product_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        # نحسب السنة اللي فاتت من ال data اللي جاي من ال wizard
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

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 35)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 25)
        worksheet.set_column('I:I', 25)


        # Formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#7FC7D9',
                                             'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        num_format = workbook.add_format({'num_format': '0.00', 'align': 'center',
                                          'valign': 'vcenter', 'border': 1})
        header_format2 = workbook.add_format({'bold': True, 'bg_color': '#2EC70A',
                                             'align': 'center', 'valign': 'vcenter', 'border': 1})


        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col, row, col + 6, f"From {date_from} To {date_to}", header_format)
        row += 1
        if date_from_last_year and date_to_last_year:
            worksheet.merge_range(row, col, row, col + 6,
                                  f"Last Year Period: From {date_from_last_year.date()} To {date_to_last_year.date()}",
                                  header_format)
            row += 2
        else:
            row += 1

        # ---------------- Table Headers ----------------
        worksheet.write(row, col, "Product Category", header_format)
        worksheet.write(row, col + 1, "Default Code", header_format)
        worksheet.write(row, col + 2, "Product", header_format)

        # هيدر السنة اللي فاتت
        worksheet.merge_range(
            row, col + 3, row, col + 5,
            f"Last Year ({date_from_last_year.date()} → {date_to_last_year.date()})",
            header_format
        )

        # الهيدر الفرعي للسنة اللي فاتت
        worksheet.write(row + 1, col + 3, "Quantity", header_format)
        worksheet.write(row + 1, col + 4, "Price", header_format)
        worksheet.write(row + 1, col + 5, "Nsap", header_format)

        # هيدر الفترة الحالية
        worksheet.merge_range(
            row, col + 6, row, col + 8,
            f"Current Period ({date_from} → {date_to})",
            header_format2
        )

        # الهيدر الفرعي للفترة الحالية
        worksheet.write(row + 1, col + 6, "Total Quantity", header_format2)
        worksheet.write(row + 1, col + 7, "Total Price", header_format2)
        worksheet.write(row + 1, col + 8, "Nsap", header_format2)

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

            worksheet.write_number(row, col + 3, record['Last Year Total Quantity'], num_format)
            worksheet.write_number(row, col + 4, record['Last Year Total Price'], num_format)
            worksheet.write_number(row, col + 5, record['Last Year Nsap'], num_format)


            worksheet.write_number(row, col + 6, record['Total Quantity'], num_format)
            worksheet.write_number(row, col + 7, record['Total Price'], num_format)
            worksheet.write_number(row, col + 8, record['Nsap'], num_format)


            row += 1
