from odoo import api, fields, models
from odoo.exceptions import UserError


class SalaryBankWizard(models.TransientModel):
    _name = "salary.bank.wizard"
    _description = "Salary Bank Wizard"

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    earn_date = fields.Date(string="تاريخ استحقاق", required=True)
    pay_date = fields.Date(string="تاريخ الصرف", required=True)

    def get_report_data(self):
        combined_data = []
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S')


        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        bank_ids = self.env['hr.payslip.run'].search([
            ('date_start', '>=', self.date_from),
            ('date_end', '<=', self.date_to),
            ('state', 'in', ['confirmed', 'transfered']),
            ('company_id', 'in', self.env.companies.ids),
        ])

        # -------------------------------
        # Loop
        # -------------------------------
        for bank in bank_ids:
            total_net_salary = sum(payslip.total_sum for payslip in bank.slip_ids)
            total_employees = len(bank.slip_ids)
            iban_sponsor = bank.iban_sponsor
            sponsor_bank_number = bank.sponsor_bank_number
            labor_office_number = bank.labor_office_number
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
                'line_ids': bank.slip_ids.ids,


            })
            print("combined_data", combined_data)
        return {'combined_data': combined_data}

    def action_print_report_text(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'vals': self.get_report_data()['combined_data'],
        }
        return self.env.ref('reports_salary_bank.report_action_salary_bank_text').report_action(self, data=data)