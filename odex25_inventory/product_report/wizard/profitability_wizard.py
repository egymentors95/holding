# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ProfitabilityWizard(models.TransientModel):
    _name = 'profitability.wizard'
    _description = 'Wizard to generate Profitability report'

    product_ids = fields.Many2many(string='Products', comodel_name='product.product')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    sales_person_ids = fields.Many2many(string='Sales Persons', comodel_name='res.users')




    def get_report_data(self):
        combined_data = []

        date_from_last_year = self.date_from - relativedelta(years=1) if self.date_from else False
        date_to_last_year = self.date_to - relativedelta(years=1) if self.date_to else False

        if self.product_ids:
            domain = [
                ('product_id', 'in', self.product_ids.ids),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
            ]
        else:
            domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
            ]

        if self.sales_person_ids:
            domain.append(('move_id.invoice_user_id', 'in', self.sales_person_ids.ids))

        product_ids = self.env['account.move.line'].search(domain).mapped('product_id')

        for product in product_ids:
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code
            sales_person_name = ''
            sales_person = False
            if self.sales_person_ids:
                sales_person = self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
                    ('parent_state', '=', 'posted'),
                    ('move_id.invoice_user_id', 'in', self.sales_person_ids.ids),
                ]).mapped('move_id.invoice_user_id')
                sales_person_name = ', '.join(sales_person.mapped('name')) if sales_person else 'N/A'
                sales_person = sales_person.id if sales_person else False

            number_of_months = 0
            if self.date_from and self.date_to:
                if self.date_from > self.date_to:
                    number_of_months = 0
                else:
                    diff = relativedelta(self.date_to, self.date_from)
                    number_of_months = diff.years * 12 + diff.months + 1
            else:
                number_of_months = 0



            plan_quantity = sum(plan.quantity_per_month for plan in self.env['sales.plan.lines'].search([
                ('product_id', '=', product.id),
                ('sales_plan_id.sales_person_id', 'in', self.sales_person_ids.ids),
                ('sales_plan_id.date_from', '<=', self.date_to),
                ('sales_plan_id.date_to', '>=', self.date_from),
                ('sales_plan_id.state', '=', 'confirmed'),

            ]))
            total_plan_quantity = plan_quantity * number_of_months if number_of_months else 0.0

            plan_price = sum(plan.price_total_per_month for plan in self.env['sales.plan.lines'].search([
                ('product_id', '=', product.id),
                ('sales_plan_id.sales_person_id', 'in', self.sales_person_ids.ids),
                ('sales_plan_id.date_from', '<=', self.date_to),
                ('sales_plan_id.date_to', '>=', self.date_from),
                ('sales_plan_id.state', '=', 'confirmed'),

            ]))
            total_plan_price = plan_price * number_of_months if number_of_months else 0.0
            plan_nasp = total_plan_price / total_plan_quantity if total_plan_quantity else 0.0

            quantity_out_invoice = sum(
                account_line.quantity
                for account_line in self.env['account.move.line'].search([
                ('product_id', '=', product.id),
                ('company_id', '=', self.env.companies.ids),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('move_id.move_type', '=', 'out_invoice'),
                ('parent_state', '=', 'posted'),
            ])
            )
            quantity_out_refund = sum(
                account_line.quantity
                for account_line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('move_id.move_type', '=', 'out_refund'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            total_quantity = quantity_out_invoice - quantity_out_refund

            price_out_invoice = sum(
                account_line.price_subtotal
                for account_line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('move_id.move_type', '=', 'out_invoice'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            price_out_refund = sum(
                account_line.price_subtotal
                for account_line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', self.date_from),
                    ('date', '<=', self.date_to),
                    ('move_id.move_type', '=', 'out_refund'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            total_price = price_out_invoice - price_out_refund
            nsap = total_price / total_quantity if total_quantity else 0.0

            qty_percentage = total_quantity / total_plan_quantity * 100 if total_plan_quantity else 0.0
            value_percentage = total_price / total_plan_price * 100 if total_plan_price else 0.0

            # ---------- نفس الفترة السنة اللي فاتت ----------
            last_year_quantity_out_invoice = sum(
                line.quantity
                for line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', date_from_last_year),
                    ('date', '<=', date_to_last_year),
                    ('move_id.move_type', '=', 'out_invoice'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            last_year_quantity_out_refund = sum(
                line.quantity
                for line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', date_from_last_year),
                    ('date', '<=', date_to_last_year),
                    ('move_id.move_type', '=', 'out_refund'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            last_year_total_quantity = last_year_quantity_out_invoice - last_year_quantity_out_refund

            last_year_price_out_invoice = sum(
                line.price_subtotal
                for line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', date_from_last_year),
                    ('date', '<=', date_to_last_year),
                    ('move_id.move_type', '=', 'out_invoice'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            last_year_price_out_refund = sum(
                line.price_subtotal
                for line in self.env['account.move.line'].search([
                    ('product_id', '=', product.id),
                    ('company_id', '=', self.env.companies.ids),
                    ('date', '>=', date_from_last_year),
                    ('date', '<=', date_to_last_year),
                    ('move_id.move_type', '=', 'out_refund'),
                    ('parent_state', '=', 'posted'),
                ])
            )
            last_year_total_price = last_year_price_out_invoice - last_year_price_out_refund
            last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0




            # Append a single row for each product, container combination
            combined_data.append({
                'Product Category': product_category,
                'Product': product_name,
                'Default Code': default_code,
                'Total Quantity': total_quantity,
                'Total Price': total_price,
                'Nsap': nsap,

                'Sales Person': sales_person_name,
                'Sales Person id': sales_person,
                #Last Year
                'Last Year Total Quantity': last_year_total_quantity,
                'Last Year Total Price': last_year_total_price,
                'Last Year Nsap': last_year_nsap,

                'Total Plan Quantity': total_plan_quantity,
                'Total Plan Price': total_plan_price,
                'Plan Nsap': plan_nasp,
                'QTY': qty_percentage,
                'Value': value_percentage,


            })

        return {
            'combined_data': combined_data,
        }


    def action_print_report_xlsx(self):
        self.ensure_one()

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],

        }

        return self.env.ref('product_report.report_action_profitability').report_action(self, data=data)

    def action_view_report(self):
        self.ensure_one()

        report_data = self.get_report_data()['combined_data']

        self.env['account.move.line2'].search([]).unlink()

        for rec in report_data:
            self.env['account.move.line2'].create({
                'product_category': rec['Product Category'],
                'product_name': rec['Product'],
                'default_code': rec['Default Code'],
                'sales_person': rec['Sales Person id'],


                'last_total_quantity': rec['Last Year Total Quantity'],
                'last_total_price': rec['Last Year Total Price'],
                'last_nsap': rec['Last Year Nsap'],

                'total_quantity': rec['Total Quantity'],
                'total_price': rec['Total Price'],
                'nsap': rec['Nsap'],

                'total_plan_quantity': rec['Total Plan Quantity'],
                'total_plan_price': rec['Total Plan Price'],
                'plan_nsap': rec['Plan Nsap'],
                'qty_percentage': rec['QTY'],
                'value_percentage': rec['Value'],
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Profitability Data',
            'res_model': 'account.move.line2',
            'view_mode': 'tree',
            'target': 'current',
        }
