from odoo import api, fields, models
from odoo.exceptions import UserError


class SalaryBankWizard(models.TransientModel):
    _name = "salary.bank.wizard"
    _description = "Salary Bank Wizard"

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    earn_date = fields.Date(string="تاريخ استحقاق", required=True)
    pay_date = fields.Date(string="تاريخ الصرف", required=True)
    sponsor_name_id = fields.Many2one(comodel_name='sponsor.name', string='اسم الكفيل')
    payment_method = fields.Selection(
        selection=[
            ('atm', 'Atm'),
            ('itqan', 'اتقان'),
        ],
        string='Payment Method',
        required=True,
        default='atm'
    )

    def get_report_data(self):
        combined_data = []
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S')


        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        bank_ids = self.env['hr.payslip.run'].sudo().search([
            ('date_start', '>=', self.date_from),
            ('date_end', '<=', self.date_to),
            ('state', 'in', ['confirmed', 'transfered']),
        ])

        # -------------------------------
        # Loop
        # -------------------------------
        for bank in bank_ids:
            slip_ids = bank.slip_ids.sudo().filtered(
                lambda slip: slip.employee_id.sponsor_name_id.id == self.sponsor_name_id.id
                             and slip.employee_id.payment_method == 'bank'
            )

            if not slip_ids:
                continue  # لو مفيش موظفين بالكفيل ده، نتخطى البنك ده

            total_net_salary = sum(slip.total_sum for slip in slip_ids)
            total_employees = len(slip_ids)
            iban_sponsor = self.sponsor_name_id.iban_number or ''
            sponsor_bank_number = self.sponsor_name_id.sponsor_bank_number
            labor_office_number = self.sponsor_name_id.labor_office_number
            currency = bank.company_id.currency_id.name



            # -------- Append --------
            combined_data.append({
                'earn_date': self.earn_date,
                'pay_date': self.pay_date,
                'total_net_salary': total_net_salary,
                'total_employees': total_employees,
                'iban_sponsor': iban_sponsor,
                'currency': currency,
                'date_time_now': date_time_now,
                'sponsor_bank_number': sponsor_bank_number,
                'labor_office_number': labor_office_number,
                'line_ids': slip_ids.ids,



            })
            if not combined_data:
                raise UserError("لا توجد بيانات لموظفين بنفس الكفيل المحدد في الفترة المحددة.")

            return {'combined_data': combined_data}

    def action_print_report_text(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'vals': self.get_report_data()['combined_data'],
        }
        return self.env.ref('reports_salary_bank.report_action_salary_bank_text').report_action(self, data=data)



    def get_report_data_itqan(self):
        combined_data = []
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S')


        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        bank_ids = self.env['hr.payslip.run'].sudo().search([
            ('date_start', '>=', self.date_from),
            ('date_end', '<=', self.date_to),
            ('state', 'in', ['confirmed', 'transfered']),
        ])

        # -------------------------------
        # Loop
        # -------------------------------
        for bank in bank_ids:
            slip_ids = bank.slip_ids.sudo().filtered(
                lambda slip: slip.employee_id.sponsor_name_id.id == self.sponsor_name_id.id
                             and slip.employee_id.payment_method == 'itqan'
            )

            if not slip_ids:
                continue

            total_net_salary = sum(slip.total_sum for slip in slip_ids)
            total_employees = len(slip_ids)
            iban_sponsor = self.sponsor_name_id.iban_number or ''
            sponsor_bank_number = self.sponsor_name_id.sponsor_bank_number
            labor_office_number = self.sponsor_name_id.labor_office_number
            currency = bank.company_id.currency_id.name



            # -------- Append --------
            combined_data.append({
                'earn_date': self.earn_date,
                'pay_date': self.pay_date,
                'total_net_salary': total_net_salary,
                'total_employees': total_employees,
                'iban_sponsor': iban_sponsor,
                'currency': currency,
                'date_time_now': date_time_now,
                'sponsor_bank_number': sponsor_bank_number,
                'labor_office_number': labor_office_number,
                'line_ids': slip_ids.ids,



            })
            if not combined_data:
                raise UserError("لا توجد بيانات لموظفين بنفس الكفيل المحدد في الفترة المحددة.")

            return {'combined_data': combined_data}

    def action_print_report_text_itqan(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'vals': self.get_report_data_itqan()['combined_data'],
        }
        return self.env.ref('reports_salary_bank.report_action_salary_bank_text_itqan').report_action(self, data=data)
