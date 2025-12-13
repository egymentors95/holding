# -*- coding: utf-8 -*-
from odoo import models, fields, api
from decimal import Decimal, ROUND_HALF_UP


class HrPayslipRunTextIqan(models.AbstractModel):
    _name = 'report.reports_salary_bank.salary_bank_text_itqan'
    _description = 'Salary Bank Text Report'

    def _fmt_amount_numeric(self, number, width):
        """ رقم عشري، آخر رقمين للكسور، بدون نقطة، وبيتم الكتابة من اليمين داخل width """
        try:
            dec = Decimal(str(number or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            s = "{:f}".format(dec).replace('.', '')
        except Exception:
            s = '0'
        return s.rjust(width, '0')[-width:]

    def _fmt_integer_right(self, number, width):
        try:
            i = int(number or 0)
            s = str(i)
        except Exception:
            s = '0'
        return s.rjust(width, '0')[-width:]

    def _fmt_string_left(self, text, width):
        if text is None:
            text = ''
        s = str(text)
        return s[:width].ljust(width, ' ')

    @api.model
    def _get_report_values(self, docids, data=None):
        vals = data.get('vals', [])
        report_lines = []

        for rec in vals:

            # ===== تفاصيل الموظفين =====
            payslips = self.env['hr.payslip'].sudo().browse(rec.get('line_ids', []))
            for slip in payslips:
                # --- السطر الأول ---
                emp_no_field = self._fmt_integer_right(slip.employee_no, 12)
                bic = (slip.employee_id.res_partner_bank_ids[:1].bank_id.bic or '').strip()
                spaces8 = ' ' * 8
                acc_number_digit = (slip.employee_id.res_partner_bank_ids[:1].acc_number or '').strip()
                acc_number = self._fmt_integer_right(acc_number_digit, 24)
                spaces11 = ' ' * 10
                emp_name = self._fmt_string_left(slip.employee_id.name, 50)
                pay_date = str(rec.get('pay_date') or '').replace('-', '')
                static_num = '2000000'
                mobile_field = slip.employee_id.mobile_phone or ''
                mobile = self._fmt_string_left(mobile_field, 10)
                # if mobile_field:
                #     mobile_field = mobile_field
                # else:
                #     mobile_field = spaces11

                # --- السطر الثاني ---
                total_sum_field = self._fmt_amount_numeric(slip.total_sum, 15)
                iqama = None
                if slip.employee_id.country_id.code == 'SA':
                    iqama = slip.employee_id.saudi_number.saudi_id
                else:
                    iqama = slip.employee_id.iqama_number.iqama_id
                employee_no_field = self._fmt_integer_right(iqama, 10)
                basic_field = self._fmt_amount_numeric(getattr(slip, 'basic_allowances', 0.0), 12)
                house_field = self._fmt_amount_numeric(getattr(slip, 'house_allowances', 0.0), 12)
                collection_trans_other = slip.other_allowances + slip.trans_allowances
                other_field = self._fmt_amount_numeric(collection_trans_other, 12)
                deduction_value = abs(getattr(slip, 'total_deductions', 0.0))
                deduction_field = self._fmt_amount_numeric(deduction_value, 12)
                five_zeros = '00000'
                spaces50 = ' ' * 50
                zero_one = '0'
                spaces30 = ' ' * 30
                company_name = self._fmt_string_left(slip.company_id.name or '', 23)
                first_line = f"{emp_no_field}{acc_number}{emp_name}{employee_no_field}{total_sum_field}{pay_date}{static_num}{spaces11}{mobile}{basic_field}{house_field}{other_field}{deduction_field}"
                report_lines.append(first_line)



        report_text = "\n".join(report_lines)
        print('teeeeeest',repr(report_text))

        return {
            'doc_ids': docids,
            'doc_model': 'salary.bank.wizard',
            'docs': self.env['salary.bank.wizard'].browse(docids),
            'data': data,
            'report_text': report_text,
        }
