from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class SalesPlan(models.Model):
    _name = 'sales.plan'
    _description = 'Sales Plan'

    name = fields.Char(string='Plan Name', compute='_compute_name', store=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    number_of_months = fields.Integer(string='Number of Months', compute='_compute_number_of_months', store=True)
    sales_person_id = fields.Many2one(comodel_name='res.users', string='Sales Person', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft')
    sales_plan_line_ids = fields.One2many(comodel_name='sales.plan.lines', inverse_name='sales_plan_id', string='Sales Plan Lines')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', default=lambda self: self.env.company)


    @api.depends('sales_person_id')
    def _compute_name(self):
        for record in self:
            if record.sales_person_id:
                record.name = record.sales_person_id.name
            else:
                record.name = ""

    @api.depends('date_from', 'date_to')
    def _compute_number_of_months(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    rec.number_of_months = 0
                else:
                    diff = relativedelta(rec.date_to, rec.date_from)
                    rec.number_of_months = diff.years * 12 + diff.months + 1
            else:
                rec.number_of_months = 0

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_set_to_draft(self):
        for record in self:
            record.state = 'draft'
