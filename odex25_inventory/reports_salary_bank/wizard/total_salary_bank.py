from odoo import models, fields, api
from odoo.exceptions import UserError


class TotalSalaryBank(models.Model):
    _name = 'total.salary.bank'
    _description = 'Total Salary Bank'

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    earn_date = fields.Date(string="تاريخ استحقاق", required=True)
    pay_date = fields.Date(string="تاريخ الصرف", required=True)
    # sponsor_name_id = fields.Many2one(comodel_name='sponsor.name', string='اسم الكفيل')
    sponsor_name_ids = fields.Many2many(comodel_name='sponsor.name', string='اسم الكفيل',)
    payment_method = fields.Selection(
        selection=[
            ('bank', 'Atm'),
            ('itqan', 'اتقان'),
        ],
        string='Payment Method',
        required=True,
        default='atm'
    )
    is_overtime = fields.Boolean()

    def get_report_data(self):
        combined_data = []
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S')


        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        Payslip = self.env['total.payslip'].sudo()

        domain = [
            ('date_from', '<=', self.date_to),
            ('date_to', '>=', self.date_from),
            ('payment_method', '=', 'bank'),
            ('sponsor_name_id', 'in', self.sponsor_name_ids.ids),
        ]

        bank_ids = Payslip.search(domain)

        if self.is_overtime:
            bank_ids = bank_ids.filtered(
                lambda b: (b.bonus or 0) > 0 or (b.overtime or 0) > 0 or (b.other_earnings or 0) > 0
            )
            bonus = sum(b.bonus for b in bank_ids)
            overtime = sum(b.overtime for b in bank_ids)
            other_earnings = sum(b.other_earnings for b in bank_ids)
            total_net_salary = bonus + overtime + other_earnings
        else:
            bonus = sum(b.bonus for b in bank_ids)
            overtime = sum(b.overtime for b in bank_ids)
            other_earnings = sum(b.other_earnings for b in bank_ids)
            net_salary = sum(b.net_salary for b in bank_ids)
            total_net_salary = net_salary - other_earnings - overtime - bonus

        total_employees = len(bank_ids)

        # -------------------------------
        # Loop
        # -------------------------------
        for bank in bank_ids:
            record = self.sponsor_name_ids[:1]
            iban_sponsor = record.iban_number or ''
            sponsor_bank_number = record.sponsor_bank_number
            labor_office_number = record.labor_office_number
            currency = bank.company_id.currency_id.name
            is_overtime = self.is_overtime


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
                'is_overtime': is_overtime,
                'line_ids': bank_ids.ids,



            })

        return {'combined_data': combined_data}

    def action_print_report_text(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'vals': self.get_report_data()['combined_data'],
        }
        return self.env.ref('reports_salary_bank.report_action_total_salary_bank_text').report_action(self, data=data)



    def get_report_data_itqan(self):
        combined_data = []
        date_time_now = fields.Datetime.now().strftime('%Y%m%d%H%M%S')


        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        Payslip = self.env['total.payslip'].sudo()

        domain = [
            ('date_from', '<=', self.date_to),
            ('date_to', '>=', self.date_from),
            ('payment_method', '=', 'itqan'),
            ('sponsor_name_id', 'in', self.sponsor_name_ids.ids),
        ]

        bank_ids = Payslip.search(domain)

        if self.is_overtime:
            bank_ids = bank_ids.filtered(
                lambda b: (b.bonus or 0) > 0 or (b.overtime or 0) > 0 or (b.other_earnings or 0) > 0
            )

            bonus = sum(b.bonus for b in bank_ids)
            overtime = sum(b.overtime for b in bank_ids)
            other_earnings = sum(b.other_earnings for b in bank_ids)
            total_net_salary = bonus + overtime + other_earnings
        else:
            bonus = sum(b.bonus for b in bank_ids)
            overtime = sum(b.overtime for b in bank_ids)
            other_earnings = sum(b.other_earnings for b in bank_ids)
            net_salary = sum(b.net_salary for b in bank_ids)
            total_net_salary = net_salary - other_earnings - overtime - bonus

        total_employees = len(bank_ids)
        for bank in bank_ids:

            record = self.sponsor_name_ids[:1]
            iban_sponsor = record.iban_itqan or ''
            sponsor_bank_number = record.sponsor_bank_number
            labor_office_number = record.labor_office_number
            currency = bank.company_id.currency_id.name
            is_overtime = self.is_overtime



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
                'is_overtime': is_overtime,
                'line_ids': bank_ids.ids,

            })

        return {'combined_data': combined_data}

    def action_print_report_text_itqan(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'vals': self.get_report_data_itqan()['combined_data'],
        }
        return self.env.ref('reports_salary_bank.report_action_total_salary_bank_text_itqan').report_action(self, data=data)
