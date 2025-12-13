from odoo import models, fields, api


class TotalPayslip(models.Model):
    _name = 'total.payslip'
    _description = 'Total Payslip'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    comp_emp_code = fields.Char(string='Company Employee Code')
    emp_name = fields.Char(string='Employee Name')
    mobile = fields.Char()
    # country_id = fields.Many2one(comodel_name='res.country', string='Country')
    id_number = fields.Char(string='ID Number')
    company_id = fields.Many2one('res.company', string='Company')
    d_name = fields.Char(string='Department Name')
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('itqan', 'اتقان')
    ], string='Payment Method')
    account_number = fields.Char(string='Account Number')
    bic = fields.Char(string='Bank Identifier Code')
    sponsor_name_id = fields.Many2one(comodel_name='sponsor.name', string='اسم الكفيل')
    sponsor_number = fields.Char(string='Sponsor Number')
    basic_salary = fields.Float(string='Basic Salary')
    transport_allowance = fields.Float(string='Transport Allowance')
    housing_allowance = fields.Float(string='Housing Allowance')
    net_salary = fields.Float(string='Net Salary')
    food_allowance = fields.Float(string='Food Allowance')
    other_allowances = fields.Float(string='Other Allowances')
    natural = fields.Float(string='Natural')
    bonus = fields.Float(string='Bonus')
    overtime = fields.Float(string='Overtime')
    overtime_vocation = fields.Float(string='Overtime Vacation')
    other_earnings = fields.Float(string='مستحقات اخرى')
    other_deductions = fields.Float(string='Other Deductions')
    loan_installment = fields.Float(string='قسط السلف')




