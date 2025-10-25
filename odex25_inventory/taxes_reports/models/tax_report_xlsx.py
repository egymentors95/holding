# -*- coding: utf-8 -*-
from odoo import models
from datetime import datetime


class TaxReportXlsx(models.AbstractModel):
    _name = 'report.taxes_reports.tax_report_xlsx'
    _description = 'Tax Report XLSX'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Tax Report')

        # تنسيقات عامة
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E1F2',
            'border': 1,
        })
        text_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        number_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        })

        # العناوين
        headers = [
            'Tax Flag Name',
            'Source',
            'Tax',
            'PER',
            'Value',
            'INV_NO',
            'Date',
            'Description_A',
            'Partner Code',
            'Partner Name',
            'Partner VAT',
        ]

        # كتابة العناوين في الصف الأول
        row = 0
        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)

        # كتابة البيانات
        invoices = data.get('invoices', [])
        row = 1

        for inv in invoices:
            sheet.write(row, 0, inv.get('tax_flag'), text_format)
            sheet.write(row, 1, inv.get('source'), text_format)
            sheet.write(row, 2, str(inv.get('tax_value') or ''), text_format)
            sheet.write(row, 3, f"{inv.get('tax_name')}%" or '', text_format)
            sheet.write(row, 4, inv.get('value') or 0.0, number_format)
            sheet.write(row, 5, inv.get('invoice_name') or '', text_format)
            sheet.write(row, 6, str(inv.get('date') or ''), text_format)
            sheet.write(row, 7, inv.get('description_note') or '', text_format)
            sheet.write(row, 8, inv.get('code') or '', text_format)
            sheet.write(row, 9, inv.get('partner_name') or '', text_format)
            sheet.write(row, 10, inv.get('partner_vat') or '', text_format)
            row += 1

        # عرض الأعمدة تلقائيًا
        for i in range(len(headers)):
            sheet.set_column(i, i, 20)
