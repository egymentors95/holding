from datetime import datetime

from odoo import models, fields, api
from collections import defaultdict

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
    deductions = fields.Float(string='خصومات')
    other_deductions = fields.Float(string='Other Deductions')
    loan_installment = fields.Float(string='قسط السلف')
    raseed_installment = fields.Float(string='رصيد السلف')
    absence_days = fields.Float(string='أيام الغياب')
    cost_absence_days = fields.Float(string='مبلغ أيام الغياب')
    insurance = fields.Float(string='تأمينات')
    total_due = fields.Float(string='Total Due', compute='_compute_total_due', store=True)
    total_deductions = fields.Float(string='اجمالي الحسميات', compute='_get_total_deductions', store=True)
    net_receivable = fields.Float(string='صافي المستحق', compute='_get_net_receivable', store=True)

    @api.depends('basic_salary', 'transport_allowance', 'housing_allowance', 'food_allowance', 'natural', 'bonus', 'overtime')
    def _compute_total_due(self):
        for record in self:
            record.total_due = (
                record.basic_salary +
                record.transport_allowance +
                record.housing_allowance +
                record.food_allowance +
                record.natural +
                record.bonus +
                record.overtime
            )

    @api.depends('loan_installment', 'raseed_installment', 'other_deductions', 'deductions', 'insurance', 'cost_absence_days')
    def _get_total_deductions(self):
        for record in self:
            record.total_deductions = (
                record.loan_installment +
                record.raseed_installment +
                record.other_deductions +
                record.deductions +
                record.cost_absence_days +
                record.insurance
            )

    @api.depends('total_deductions', 'total_due')
    def _get_net_receivable(self):
        for rec in self:
            rec.net_receivable = rec.total_due - rec.total_deductions




class ReportTotalPayslip(models.AbstractModel):
    _name = 'report.reports_salary_bank.total_payslip_report'
    _description = 'Total Payslip Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        records = self.env['total.payslip'].browse(docids)

        # تجميع حسب القسم
        departments = defaultdict(list)
        for rec in records:
            departments[rec.d_name or 'بدون قسم'].append(rec)

        # أسماء الشهور بالعربي
        arabic_months = {
            1: 'يناير',
            2: 'فبراير',
            3: 'مارس',
            4: 'أبريل',
            5: 'مايو',
            6: 'يونيو',
            7: 'يوليو',
            8: 'أغسطس',
            9: 'سبتمبر',
            10: 'أكتوبر',
            11: 'نوفمبر',
            12: 'ديسمبر'
        }

        today = datetime.now()

        # اسم الشركة من أول سجل
        company_name = records[0].company_id.name if records else ''

        return {
            'docs': records,
            'departments': departments,
            'month_name': arabic_months[today.month],
            'year': today.year,
            'company_name': company_name,
        }

