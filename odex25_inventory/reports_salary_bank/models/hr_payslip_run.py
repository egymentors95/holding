from odoo import api, fields, models


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    sponsor_name_id = fields.Many2one(comodel_name='sponsor.name', string='اسم الكفيل', compute='_compute_sponsor_name', store=True)
    iban_sponsor = fields.Char(string='IBAN الكفيل', compute='_compute_iban_sponsor', store=True)
    sponsor_bank_number = fields.Char(string='رقم حساب الكفيل', compute='_compute_iban_sponsor', store=True)
    labor_office_number = fields.Char(string='رقم مكتب العمل', compute='_compute_labor_office_number', store=True)

    @api.depends('slip_ids.employee_id.sponsor_name_id', 'slip_ids', 'slip_ids.employee_id')
    def _compute_sponsor_name(self):
        for record in self:
            sponsor_names = record.slip_ids.mapped('employee_id.sponsor_name_id')
            sponsor_names = [s for s in sponsor_names if s]
            record.sponsor_name_id = sponsor_names[0] if sponsor_names else False

    @api.depends('sponsor_name_id', 'sponsor_name_id.iban_number')
    def _compute_iban_sponsor(self):
        for record in self:
            record.iban_sponsor = record.sponsor_name_id.iban_number if record.sponsor_name_id else ''

    @api.depends('sponsor_name_id', 'sponsor_name_id.sponsor_bank_number')
    def _compute_sponsor_bank_number(self):
        for record in self:
            record.sponsor_bank_number = record.sponsor_name_id.sponsor_bank_number if record.sponsor_name_id else ''

    @api.depends('sponsor_name_id', 'sponsor_name_id.labor_office_number')
    def _compute_labor_office_number(self):
        for record in self:
            record.labor_office_number = record.sponsor_name_id.labor_office_number if record.sponsor_name_id else ''