# -*- coding: utf-8 -*-
from odoo import models, fields, api
from decimal import Decimal, ROUND_HALF_UP


class HrPayslipRunText(models.AbstractModel):
    _name = 'report.reports_salary_bank.salary_bank_text'
    _description = 'Salary Bank Text Report'

    def _fmt_amount_numeric(self, number, width):
        """
        Round to 2 decimals, remove decimal point, pad with zeros on the LEFT (i.e. numeric right-aligned)
        Example: 152.9542 -> round->152.95 -> '15295' -> rjust(width,'0')
        """
        try:
            dec = Decimal(str(number or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            # remove decimal point
            s = "{:f}".format(dec)  # '152.95' or '95478621.12'
            s = s.replace('.', '')  # '15295' or '9547862112'
        except Exception:
            s = '0'
        return s.rjust(width, '0')[-width:]

    def _fmt_integer_right(self, number, width):
        """
        integer numeric right padded with zeros from left
        """
        try:
            i = int(number or 0)
            s = str(i)
        except Exception:
            s = '0'
        return s.rjust(width, '0')[-width:]

    def _fmt_string_left(self, text, width):
        """
        plain string, left-justified, pad with spaces to width (or with zeros if needed by spec).
        Use for names and fields that should be left->right.
        """
        if text is None:
            text = ''
        s = str(text)
        # truncate if longer
        if len(s) > width:
            return s[:width]
        return s.ljust(width, ' ')

    def _fmt_string_zero_left(self, text, width):
        """
        treat text as string and pad on the RIGHT with zeros (used earlier for labor_office_number?).
        But per spec: labor_office_number -> 18 chars left-to-right (left-justified) with zeros.
        sponsor_bank_number: numeric padding from RIGHT to LEFT (we will use numeric right formatter).
        """
        if text is None:
            text = ''
        s = str(text)
        return s.ljust(width, '0')[:width]

    @api.model
    def _get_report_values(self, docids, data=None):
        # ensure data available
        if not data:
            data = {}
        vals = data.get('vals') or []
        report_lines = []

        for rec in vals:
            # header
            # 12 zeros + 'G' + earn_date + pay_date
            earn_date = ''
            pay_date = ''
            if rec.get('earn_date'):
                # could be date or string
                v = rec.get('earn_date')
                try:
                    earn_date = v.strftime('%Y%m%d') if hasattr(v, 'strftime') else str(v).replace('-', '')
                except Exception:
                    earn_date = str(v).replace('-', '')
            if rec.get('pay_date'):
                v = rec.get('pay_date')
                try:
                    pay_date = v.strftime('%Y%m%d') if hasattr(v, 'strftime') else str(v).replace('-', '')
                except Exception:
                    pay_date = str(v).replace('-', '')

            # total_net_salary: 15 chars numeric, last two digits decimals (rounded)
            total_net_salary_field = self._fmt_amount_numeric(rec.get('total_net_salary', 0.0), 15)

            # total_employees: 9 digits, right aligned numeric
            total_employees_field = self._fmt_integer_right(rec.get('total_employees', 0), 9)

            iban_sponsor = rec.get('iban_sponsor') or ''
            currency = rec.get('currency') or ''

            date_time_now = rec.get('date_time_now') or fields.Datetime.now().strftime('%Y%m%d%H%M%S')

            # sponsor_bank_number: numeric field, 16 digits — fill from RIGHT (so use _fmt_integer_right but if sponsor_bank_number contain non-digits, strip non digits)
            sponsor_bn = rec.get('sponsor_bank_number') or ''
            sponsor_bn_digits = ''.join(ch for ch in str(sponsor_bn) if ch.isdigit())
            sponsor_bank_number_field = sponsor_bn_digits.rjust(16, '0')[-16:] if sponsor_bn_digits else '0' * 16

            # labor_office_number: 18 characters left-to-right (per your request)
            labor_office_number_field = self._fmt_string_zero_left(rec.get('labor_office_number') or '', 18)

            # header assembly
            header = (
                f"{'0'*12}G{earn_date}{pay_date}"
                f"{total_net_salary_field}{total_employees_field}"
                f"{iban_sponsor}{currency}E01{date_time_now}"
                f"{sponsor_bank_number_field}{labor_office_number_field}"
                f"{' '*11}PAYR{' '*6}Payroll"
            )
            report_lines.append(header)

            # lines -> get hr.payslip records from ids
            line_ids = rec.get('line_ids') or []
            # if line_ids may already be recordset, handle both:
            payslip_ids = []
            if isinstance(line_ids, (list, tuple)):
                payslip_ids = [int(x) for x in line_ids if str(x).isdigit()]
            else:
                # if it's hr.payslip(...) or recordset - convert
                try:
                    # if recordset-like string, ignore; safe fallback: treat as empty
                    payslip_ids = []
                except Exception:
                    payslip_ids = []

            payslips = self.env['hr.payslip'].sudo().browse(payslip_ids)

            for slip in payslips:
                # first line for employee:
                # 12 zeros field for employee_no (right aligned)
                emp_no_val = getattr(slip, 'employee_no', None) or getattr(slip.employee_id, 'emp_no', None) or getattr(slip.employee_id, 'employee_no', None) or slip.employee_id.id
                emp_no_field = self._fmt_integer_right(emp_no_val, 12)

                # 8 spaces
                spaces8 = ' ' * 8

                # bank account (account number) from employee res_partner_bank_ids first item acc_number (no spaces trimming)
                acc_number = ''
                try:
                    bank_obj = slip.employee_id.res_partner_bank_ids[:1]
                    acc_number = bank_obj.acc_number or ''
                except Exception:
                    acc_number = ''
                acc_number = str(acc_number).strip()
                # bank account is variable length — in samples it looks like 22 or so, we will keep it as-is (no extra formatting)
                # then 11 spaces
                spaces11 = ' ' * 11

                # employee name left-justified
                employee_name = slip.employee_id.name or ''
                # assemble first line
                first_line = f"{emp_no_field}{spaces8}{acc_number}{spaces11}{employee_name}"
                report_lines.append(first_line)

                # second line:
                # total_sum: 10 digits, right aligned, last two digits decimals
                total_sum_field = self._fmt_amount_numeric(getattr(slip, 'total_sum', 0.0), 10)

                # id_number: 10 digits field (identity). take employee.identification_id
                id_number_raw = getattr(slip.employee_id, 'identification_id', '') or ''
                # remove non-digits and keep right-aligned
                id_digits = ''.join(ch for ch in str(id_number_raw) if ch.isdigit())
                id_field = id_digits.rjust(10, '0')[-10:] if id_digits else '0' * 10

                # basic salary: 18 digits numeric (round 2 decimals, no dot)
                basic_salary_field = self._fmt_amount_numeric(getattr(slip, 'basic_salary', 0.0), 18)

                # house allowance: 12 digits
                house_allowance_field = self._fmt_amount_numeric(getattr(slip, 'house_allowance', getattr(slip, 'house_allowances', 0.0)), 12)

                # total_deductions: 12 digits
                deductions_field = self._fmt_amount_numeric(getattr(slip, 'total_deductions', 0.0), 12)

                # currency
                currency_field = currency

                # 50 spaces then '0' then 30 spaces then company name
                spaces50 = ' ' * 50
                zero_one = '0'
                spaces30 = ' ' * 30
                company_name = slip.company_id.name or ''

                second_line = (
                    f"{total_sum_field}{id_field}{basic_salary_field}{house_allowance_field}"
                    f"{deductions_field}{currency_field}{spaces50}{zero_one}{spaces30}{company_name}"
                )
                report_lines.append(second_line)

        report_text = "".join(line + "\n" for line in report_lines).lstrip()

        return {
            'doc_ids': docids,
            'doc_model': 'salary.bank.wizard',
            'docs': self.env['salary.bank.wizard'].browse(docids),
            'data': data,
            'report_text': report_text,
        }
