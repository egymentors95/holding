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
    product_category_ids = fields.Many2many(string='Product Categories', comodel_name='product.category')

    def get_report_data(self):
        combined_data = []

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        # فترات السنة اللي فاتت
        date_from_last_year = self.date_from - relativedelta(years=1) if self.date_from else False
        date_to_last_year = self.date_to - relativedelta(years=1) if self.date_to else False

        # -------------------------------
        # جلب كل خطوط الفواتير مرة واحدة
        # -------------------------------
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.sales_person_ids:
            domain.append(('move_id.invoice_user_id', 'in', self.sales_person_ids.ids))
        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        lines = self.env['account.move.line'].search(domain)

        # -------------------------------
        # جلب خطوط السنة اللي فاتت مرة واحدة
        # -------------------------------
        last_year_lines = self.env['account.move.line'].search([
            ('date', '>=', date_from_last_year),
            ('date', '<=', date_to_last_year),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ])

        # -------------------------------
        # Loop على المنتجات
        # -------------------------------
        for product in lines.mapped('product_id'):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code or ''

            # لو فيه أكتر من Sales Person
            for sales_person in product_lines.mapped('move_id.invoice_user_id'):
                sales_lines = product_lines.filtered(lambda l: l.move_id.invoice_user_id == sales_person)

                # -------- خطط المبيعات --------
                number_of_months = 0
                if self.date_from and self.date_to:
                    diff = relativedelta(self.date_to, self.date_from)
                    number_of_months = diff.years * 12 + diff.months + 1

                plan_lines = self.env['sales.plan.lines'].search([
                    ('product_id', '=', product.id),
                    ('sales_plan_id.sales_person_id', '=', sales_person.id),
                    ('sales_plan_id.date_from', '<=', self.date_to),
                    ('sales_plan_id.date_to', '>=', self.date_from),
                    ('sales_plan_id.state', '=', 'confirmed'),
                ])

                plan_quantity = sum(plan_lines.mapped('quantity_per_month'))
                total_plan_quantity = plan_quantity * number_of_months if number_of_months else 0.0

                plan_price = sum(plan_lines.mapped('price_total_per_month'))
                total_plan_price = plan_price * number_of_months if number_of_months else 0.0

                plan_nasp = total_plan_price / total_plan_quantity if total_plan_quantity else 0.0

                # -------- المبيعات الحالية --------
                qty_out_invoice = sum(sales_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
                qty_out_refund = sum(sales_lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('quantity'))
                total_quantity = qty_out_invoice - qty_out_refund

                price_out_invoice = sum(sales_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('price_subtotal'))
                price_out_refund = sum(sales_lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('price_subtotal'))
                total_price = price_out_invoice - price_out_refund

                nsap = total_price / total_quantity if total_quantity else 0.0

                qty_percentage = total_quantity / total_plan_quantity * 100 if total_plan_quantity else 0.0
                value_percentage = total_price / total_plan_price * 100 if total_plan_price else 0.0

                # -------- السنة اللي فاتت --------
                last_year_sales = last_year_lines.filtered(lambda l: l.product_id == product and l.move_id.invoice_user_id == sales_person)

                last_qty_out_invoice = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
                last_qty_out_refund = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('quantity'))
                last_year_total_quantity = last_qty_out_invoice - last_qty_out_refund

                last_price_out_invoice = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('price_subtotal'))
                last_price_out_refund = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('price_subtotal'))
                last_year_total_price = last_price_out_invoice - last_price_out_refund

                last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0

                # -------- Append --------
                combined_data.append({
                    'Product Category': product_category,
                    'Product': product_name,
                    'Default Code': default_code,
                    'Sales Person': sales_person.name,
                    'Sales Person id': sales_person.id,

                    'Total Quantity': total_quantity,
                    'Total Price': total_price,
                    'Nsap': nsap,

                    'Last Year Total Quantity': last_year_total_quantity,
                    'Last Year Total Price': last_year_total_price,
                    'Last Year Nsap': last_year_nsap,

                    'Total Plan Quantity': total_plan_quantity,
                    'Total Plan Price': total_plan_price,
                    'Plan Nsap': plan_nasp,

                    'QTY': qty_percentage,
                    'Value': value_percentage,
                })

        return {'combined_data': combined_data}

    def action_print_report_xlsx(self):
        self.ensure_one()
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
