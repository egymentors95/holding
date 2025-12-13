# -*- coding: utf-8 -*-
from odoo import models, fields, api
from decimal import Decimal, ROUND_HALF_UP


class HrPayslipRunText(models.AbstractModel):
    _name = 'report.reports_salary_bank.total_salary_bank_text'
    _description = ' Total Salary Bank Text Report'

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
        # ===== الهيدر =====
        earn_date = str(rec.get('earn_date') or '').replace('-', '')
        pay_date = str(rec.get('pay_date') or '').replace('-', '')
        total_net_salary_field = self._fmt_amount_numeric(rec.get('total_net_salary', 0.0), 15)
        total_employees_field = self._fmt_integer_right(rec.get('total_employees', 0), 8)
        iban_sponsor = rec.get('iban_sponsor') or ''
        currency = rec.get('currency') or ''
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S') + '16'
        sponsor_bn_digits = ''.join(ch for ch in str(rec.get('sponsor_bank_number') or '') if ch.isdigit())
        sponsor_bank_number_field = sponsor_bn_digits.rjust(16, '0')[-16:]
        labor_office_number_field = self._fmt_string_left(rec.get('labor_office_number') or '', 18)
        is_overtime = rec.get('is_overtime')

        header = (
            f"{'0'*12}G{earn_date}{pay_date}"
            f"{total_net_salary_field}{total_employees_field}"
            f"{iban_sponsor}{currency}E01{date_time_now}"
            f"{sponsor_bank_number_field}{labor_office_number_field}"
            f"PAYR{' '*6}Payroll{' '*151}"
        )
        report_lines.append(header)

        # ===== تفاصيل الموظفين =====
        payslips = self.env['total.payslip'].browse(rec.get('line_ids', []))
        print('payslips', payslips)

        for slip in payslips:
            # --- السطر الأول ---
            emp_no_field = self._fmt_integer_right(slip.comp_emp_code, 12)
            bic = (slip.bic or '').strip()
            spaces8 = ' ' * 8
            acc_number = (slip.account_number or '').strip()
            spaces11 = ' ' * 11
            emp_name = self._fmt_string_left(slip.emp_name, 50)


            if not is_overtime:
            # --- السطر الثاني ---
                net_salary = slip.net_salary - slip.bonus - slip.overtime - slip.other_earnings
                total_sum_field = self._fmt_amount_numeric(net_salary, 15)
                basic_field = self._fmt_amount_numeric(getattr(slip, 'basic_salary', 0.0), 18)
                house_field = self._fmt_amount_numeric(getattr(slip, 'housing_allowance', 0.0), 12)
                collection_trans_other = slip.other_allowances + slip.transport_allowance + slip.food_allowance + slip.natural
                other_field = self._fmt_amount_numeric(collection_trans_other, 12)
                deduction_value = abs(getattr(slip, 'other_deductions', 0.0)) + abs(getattr(slip, 'loan_installment', 0.0))
                deduction_field = self._fmt_amount_numeric(deduction_value, 12)
            else:
                new_net_salary = slip.bonus + slip.overtime + slip.other_earnings
                total_sum_field = self._fmt_amount_numeric(new_net_salary, 15)
                basic_field = self._fmt_amount_numeric(new_net_salary,  18)
                house_field = self._fmt_amount_numeric( 0.0, 12)
                other_field = self._fmt_amount_numeric(0, 12)
                deduction_field = self._fmt_amount_numeric(0, 12)



            iqama = slip.id_number
            employee_no_field = self._fmt_integer_right(iqama, 10)
            currency_field = currency
            five_zeros = '00000'
            spaces50 = ' ' * 50
            zero_one = '0'
            spaces30 = ' ' * 30
            company_name = self._fmt_string_left(slip.company_id.name or '', 23)
            first_line = f"{emp_no_field}{bic}{spaces8}{acc_number}{spaces11}{emp_name}{total_sum_field}{employee_no_field}{basic_field}{house_field}{other_field}{deduction_field}{currency_field}{five_zeros}{spaces50}{zero_one}{spaces30}{company_name}"
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
