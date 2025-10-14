from odoo import models
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource


class SalesPartnerReport(models.AbstractModel):
    _name = 'report.sales_partner_report.sales_partner_report_xlsx'
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

        worksheet = workbook.add_worksheet('Sales Partner Report')
        row = 0
        col = 0

        worksheet.set_column('A:A', 17)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 12)
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
        header_format6 = workbook.add_format({'bold': True, 'bg_color': '#f0f0f0', 'num_format': '#,##0.00',
                                             'align': 'center', 'valign': 'vcenter', 'border': 2})
        header_format7 = workbook.add_format({'bold': True, 'bg_color': '#27F53C',
                                             'align': 'left', 'valign': 'vcenter', 'border': 2})
        header_format8 = workbook.add_format({'bold': True, 'bg_color': '#27C2F5', 'num_format': '#,##0.00',
                                              'align': 'center', 'valign': 'vcenter', 'border': 2})


        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter','num_format': '#,##0.00',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})
        cell_format1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                           'border': 0, 'left': 2, 'right': 2, 'top': 1, 'bottom': 1})


        logo_path = get_module_resource('sales_partner_report', 'static/img', 'logo.png')
        if logo_path:
            worksheet.insert_image(0, 4, logo_path, {
                'x_scale': .88,
                'y_scale': 0.190,
            })


        # ---------------- Header with dates ----------------
        worksheet.merge_range(row, col + 2, row + 4, col + 8, "")

        worksheet.write(row, col, f"Report", header_format0)
        worksheet.write(row, col + 1, f"Sales Partner Report", header_format0)
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

        # sales_partners = list(set([rec['Partner'] for rec in lots_data])) or ["No Partner"]
        group_mode = self.env.context.get('group_mode', 'partners')

        if group_mode == 'category':
            # اجمع حسب تصنيف الشركاء
            group_entities = list(set([rec['Partner Category'] for rec in lots_data])) or ["No Category"]
        else:
            # اجمع حسب الشريك نفسه
            group_entities = list(set([rec['Partner'] for rec in lots_data])) or ["No Partner"]

        for group_entity in group_entities:
            # عنوان Sales Person
            worksheet.merge_range(row, col, row, col + 8, f"{'Partner Category' if group_mode == 'category' else 'Partner'}: {group_entity}",header_format7)
            row += 2

            # Table Headers
            worksheet.merge_range(row, col, row+1, col, "Product Category", header_format)
            worksheet.merge_range(row, col + 1, row+1, col + 1, "Default Code", header_format)
            worksheet.merge_range(row, col + 2, row+1, col + 2, "Product", header_format)

            worksheet.merge_range(
                row, col + 3, row, col + 5,
                f"Last ({date_from_last_year.date()} → {date_to_last_year.date()})",
                header_format2
            )
            worksheet.write(row + 1, col + 3, "QTY", header_format2)
            worksheet.write(row + 1, col + 4, "Value", header_format2)
            worksheet.write(row + 1, col + 5, "NASP", header_format2)

            worksheet.merge_range(
                row, col + 6, row, col + 8,
                f"Current ({date_from} → {date_to})",
                header_format3
            )
            worksheet.write(row + 1, col + 6, "Total QTY", header_format3)
            worksheet.write(row + 1, col + 7, "Total Value", header_format3)
            worksheet.write(row + 1, col + 8, "NASP", header_format3)

            row += 2

            # Data Rows for this Sales Person
            last_category = None
            category_totals = {'Last Year Total Price': 0, 'Total Price': 0,
                              }
            grand_totals = {'Last Year Total Price': 0, 'Total Price': 0,
                           }

            if group_mode == 'category':
                person_records = [rec for rec in lots_data if rec['Partner Category'] == group_entity]
            else:
                person_records = [rec for rec in lots_data if rec['Partner'] == group_entity]

            for record in person_records:
                if record['Product Category'] != last_category:
                    if last_category:
                        # subtotal
                        worksheet.merge_range(row, col, row, col + 2, f"Subtotal", header_format)
                        worksheet.write(row, col + 3, '', header_format6)
                        worksheet.write_number(row, col + 4, category_totals['Last Year Total Price'], header_format6)
                        worksheet.write(row, col + 5, '', header_format6)
                        worksheet.write(row, col + 6, '', header_format6)
                        worksheet.write_number(row, col + 7, category_totals['Total Price'], header_format6)
                        worksheet.write(row, col + 8, '', header_format6)

                        row += 1

                        for key in grand_totals:
                            grand_totals[key] += category_totals[key]
                        category_totals = {k: 0 for k in category_totals}

                    worksheet.merge_range(row, col, row, col + 8, record['Product Category'], header_format0)
                    last_category = record['Product Category']
                    row += 1

                # تفاصيل المنتج
                worksheet.write(row, col, "", cell_format1)
                worksheet.write(row, col + 1, record['Default Code'] or '', cell_format1)
                worksheet.write(row, col + 2, record['Product'] or '', cell_format1)

                worksheet.write_number(row, col + 3, record['Last Year Total Quantity'], cell_format)
                worksheet.write_number(row, col + 4, record['Last Year Total Price'], cell_format)
                worksheet.write_number(row, col + 5, record['Last Year Nsap'], cell_format)

                worksheet.write_number(row, col + 6, record['Total Quantity'], cell_format)
                worksheet.write_number(row, col + 7, record['Total Price'], cell_format)
                worksheet.write_number(row, col + 8, record['Nsap'], cell_format)

                category_totals['Last Year Total Price'] += record['Last Year Total Price'] or 0
                category_totals['Total Price'] += record['Total Price'] or 0
                row += 1

            # subtotal آخر كاتيجوري
            if last_category:
                worksheet.merge_range(row, col, row, col + 2, f"Subtotal", header_format)
                worksheet.write(row, col + 3, '', header_format6)
                worksheet.write_number(row, col + 4, category_totals['Last Year Total Price'], header_format6)
                worksheet.write(row, col + 5, '', header_format6)
                worksheet.write(row, col + 6, '', header_format6)
                worksheet.write_number(row, col + 7, category_totals['Total Price'], header_format6)
                worksheet.write(row, col + 8, '', header_format6)
                row += 1

                for key in grand_totals:
                    grand_totals[key] += category_totals[key]

            # Grand total للسيلز بيرسون
            worksheet.merge_range(row, col, row, col + 2, "Grand Total", header_format8)
            worksheet.write(row, col + 3, '', header_format8)
            worksheet.write_number(row, col + 4, grand_totals['Last Year Total Price'], header_format8)
            worksheet.write(row, col + 5, '', header_format8)
            worksheet.write(row, col + 6, '', header_format8)
            worksheet.write_number(row, col + 7, grand_totals['Total Price'], header_format8)
            worksheet.write(row, col + 8, '', header_format8)
            row += 3  # مسافة بين كل Sales Person والتاني

