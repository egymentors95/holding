# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ProfitReportWizard(models.TransientModel):
    _name = 'profit.report.wizard'
    _description = 'Profit Report Wizard'

    product_ids = fields.Many2many(string='Products', comodel_name='product.product')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
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
        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
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
        ])


        # -------------------------------
        # Loop على المنتجات
        # -------------------------------
        for product in lines.mapped('product_id'):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code or ''


            # -------- المبيعات الحالية --------
            qty_out_invoice = sum(product_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
            qty_out_refund = sum(product_lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('quantity'))
            total_quantity = qty_out_invoice - qty_out_refund

            price_out_invoice = sum(product_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('price_subtotal'))
            price_out_refund = sum(lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('price_subtotal'))
            total_price = price_out_invoice - price_out_refund

            nsap = total_price / total_quantity if total_quantity else 0.0


            # -------- السنة اللي فاتت --------
            last_year_sales = last_year_lines.filtered(lambda l: l.product_id == product)

            last_qty_out_invoice = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
            last_qty_out_refund = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('quantity'))
            last_year_total_quantity = last_qty_out_invoice - last_qty_out_refund

            last_price_out_invoice = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('price_subtotal'))
            last_price_out_refund = sum(last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('price_subtotal'))
            last_year_total_price = last_price_out_invoice - last_price_out_refund

            last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0

            # -------- المشتريات الحالية --------
            qty_in_invoice = sum(
                product_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
            qty_in_refund = sum(product_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
            total_quantity_invoice = qty_in_invoice - qty_in_refund

            price_in_invoice = sum(
                product_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
            price_in_refund = sum(
                product_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
            total_price_invoice = price_in_invoice - price_in_refund

            naap = total_price_invoice / total_quantity_invoice if total_quantity_invoice else 0.0

            # -------- السنة اللي فاتت --------
            last_year_purchases = last_year_lines.filtered(
                lambda l: l.product_id == product)

            last_qty_in_invoice = sum(
                last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
            last_qty_in_refund = sum(
                last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
            last_year_total_quantity_invoice = last_qty_in_invoice - last_qty_in_refund

            last_price_in_invoice = sum(
                last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
            last_price_in_refund = sum(
                last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
            last_year_total_price_invoice = last_price_in_invoice - last_price_in_refund

            last_year_naap = last_year_total_price_invoice / last_year_total_quantity_invoice if last_year_total_quantity_invoice else 0.0

            #_________________________________________________________________________________________
            margin = nsap - naap
            profit_value = margin * total_quantity_invoice
            last_margin = last_year_nsap - last_year_naap
            last_profit_value = last_margin * last_year_total_quantity_invoice


            # -------- Append --------
            combined_data.append({
                'Product Category': product_category,
                'Product': product_name,
                'Default Code': default_code,

                'Total Quantity': total_quantity,
                'Total Price': total_price,
                'Nsap': nsap,
                'Naap': naap,
                'Profit Value': profit_value,
                'Margin': margin,


                'Last Year Total Quantity': last_year_total_quantity,
                'Last Year Total Price': last_year_total_price,
                'Last Year Nsap': last_year_nsap,
                'Last Year Naap': last_year_naap,
                'Last Profit Value': last_profit_value,
                'Last Margin': last_margin,



            })

        return {'combined_data': combined_data}

    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('profit_report.report_action_profit_report_wizard').report_action(self, data=data)

    def action_view_report(self):
        self.ensure_one()
        report_data = self.get_report_data()['combined_data']

        self.env['account.move.line4'].search([]).unlink()

        for rec in report_data:
            self.env['account.move.line4'].create({
                'product_category': rec['Product Category'],
                'product_name': rec['Product'],
                'default_code': rec['Default Code'],

                'last_total_quantity': rec['Last Year Total Quantity'],
                'last_total_price': rec['Last Year Total Price'],
                'last_nsap': rec['Last Year Nsap'],

                'total_quantity': rec['Total Quantity'],
                'total_price': rec['Total Price'],
                'nsap': rec['Nsap'],

                'naap': rec['Naap'],
                'last_year_naap': rec['Last Year Naap'],

                'margin': rec['Margin'],
                'last_margin': rec['Last Margin'],

                'profit_value': rec['Profit Value'],
                'last_profit_value': rec['Last Profit Value'],

            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Profit Report Views',
            'res_model': 'account.move.line4',
            'view_mode': 'tree',
            'target': 'current',
        }
