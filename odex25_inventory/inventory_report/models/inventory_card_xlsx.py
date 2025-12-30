# -*- coding: utf-8 -*-
from odoo import models


class InventoryCardXlsx(models.AbstractModel):
    _name = 'report.inventory_report.inventory_card_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Inventory Card')

        # Formats
        header = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        cell = workbook.add_format({'border': 1})
        center = workbook.add_format({'border': 1, 'align': 'center'})
        number = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})

        # -------------------------------------------------
        # Columns Order
        # -------------------------------------------------
        columns = [
            'Date',
            'المنتج',
            'فئة المنتج',
            'نوع الحركة',
            'الكمية الواردة',
            'الكمية المنصرفة',
            # 'رصيد المخزن قبل الحركة',
            'رصيد المخزن بعد الحركة',
            'متوسط التكلفة',
            'اجمالي تكلفة الرصيد',
        ]

        # Write Header
        for col, title in enumerate(columns):
            sheet.write(0, col, title, header)
            sheet.set_column(col, col, 22)

        row = 1

        # -------------------------------------------------
        # Data Rows
        # -------------------------------------------------
        for line in data.get('lines', []):
            sheet.write(row, 0, line['date'], center)
            sheet.write(row, 1, line['product'], cell)
            sheet.write(row, 2, line['category'], cell)
            sheet.write(row, 3, line['picking_type'], cell)

            sheet.write(row, 4, line['qty_in'], number)
            sheet.write(row, 5, line['qty_out'], number)
            # sheet.write(row, 6, line['qty_before'], number)
            sheet.write(row, 6, line['qty_after'], number)
            sheet.write(row, 7, line['avg_cost'], number)
            sheet.write(row, 8, line['total_cost'], number)

            row += 1
