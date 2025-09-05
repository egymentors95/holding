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




    def get_report_data(self):
        combined_data = []

        date_from_last_year = self.date_from - relativedelta(years=1) if self.date_from else False
        date_to_last_year = self.date_to - relativedelta(years=1) if self.date_to else False

        if self.product_ids:
            product_ids = self.product_ids
        else:
            product_ids = self.env['product.product'].search([])


        for product in product_ids:
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code




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
                #Last Year
                'Last Year Total Quantity': last_year_total_quantity,
                'Last Year Total Price': last_year_total_price,
                'Last Year Nsap': last_year_nsap,


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

                'last_total_quantity': rec['Last Year Total Quantity'],
                'last_total_price': rec['Last Year Total Price'],
                'last_nsap': rec['Last Year Nsap'],

                'total_quantity': rec['Total Quantity'],
                'total_price': rec['Total Price'],
                'nsap': rec['Nsap'],
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Profitability Data',
            'res_model': 'account.move.line2',
            'view_mode': 'tree',
            'target': 'current',
        }
