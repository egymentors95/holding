# -*- coding: utf-8 -*-
from odoo import models, fields, api
from decimal import Decimal, ROUND_HALF_UP


class HrPayslipRunTextIqan(models.AbstractModel):
    _name = 'report.reports_salary_bank.total_salary_bank_itqan_text'
    _description = 'Total Salary Bank Text Itqan Report'

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

        if not vals:
            return {}

        rec = vals[0]

            # ===== تفاصيل الموظفين =====
        payslips = self.env['total.payslip'].browse(rec.get('line_ids', []))
        is_overtime = rec.get('is_overtime')
        for slip in payslips:
            # --- السطر الأول ---
            emp_no_field = self._fmt_integer_right(slip.comp_emp_code, 12)
            acc_number_digit = (slip.account_number or '').strip()
            acc_number = self._fmt_integer_right(acc_number_digit, 24)
            spaces11 = ' ' * 10
            emp_name = self._fmt_string_left(slip.emp_name, 50)
            pay_date = str(rec.get('pay_date') or '').replace('-', '')
            static_num = '2000000'
            mobile_field = slip.mobile or ''
            mobile = self._fmt_string_left(mobile_field, 10)

            if not is_overtime:
                net_salary = slip.net_salary - slip.bonus - slip.overtime - slip.other_earnings
                total_sum_field = self._fmt_amount_numeric(net_salary, 15)
                basic_field = self._fmt_amount_numeric(getattr(slip, 'basic_salary', 0.0), 12)
                house_field = self._fmt_amount_numeric(getattr(slip, 'housing_allowance', 0.0), 12)
                collection_trans_other = slip.other_allowances + slip.transport_allowance + slip.food_allowance + slip.natural
                other_field = self._fmt_amount_numeric(collection_trans_other, 12)
                deduction_value = abs(getattr(slip, 'other_deductions', 0.0)) + abs(getattr(slip, 'loan_installment', 0.0))
                deduction_field = self._fmt_amount_numeric(deduction_value, 12)
            else:
                new_net_salary = slip.bonus + slip.overtime + slip.other_earnings
                total_sum_field = self._fmt_amount_numeric(new_net_salary, 15)
                basic_field = self._fmt_amount_numeric(new_net_salary,  12)
                house_field = self._fmt_amount_numeric( 0.0, 12)
                other_field = self._fmt_amount_numeric(0, 12)
                deduction_field = self._fmt_amount_numeric(0, 12)

            iqama = slip.id_number
            employee_no_field = self._fmt_integer_right(iqama, 10)
            first_line = f"{emp_no_field}{acc_number}{emp_name}{employee_no_field}{total_sum_field}{pay_date}{static_num}{spaces11}{mobile}{basic_field}{house_field}{other_field}{deduction_field}"
            report_lines.append(first_line)



        report_text = "\n".join(report_lines)
        print('teeeeeest',repr(report_text))

        return {
            'doc_ids': docids,
            'doc_model': 'total.salary.bank',
            'docs': self.env['total.salary.bank'].browse(docids),
            'data': data,
            'report_text': report_text,
        }
