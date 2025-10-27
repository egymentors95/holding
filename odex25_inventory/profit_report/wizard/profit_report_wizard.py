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
    # is_partner = fields.Boolean(string='Is Partner', default=False)
    groub_by_partner = fields.Selection([
        ('partners', 'Partners'),
        ('category', 'Category'),
    ], string='Group by Partner', default='partners')
    partner_ids = fields.Many2many(string='Partners', comodel_name='res.partner')
    partner_category_ids = fields.Many2many(string='Partner Categories', comodel_name='partner.category')


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
            ('account_id.internal_group', '=', 'income'),

        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
        if self.partner_ids:
            domain.append(('move_id.partner_id', 'in', self.partner_ids.ids))
        if self.partner_category_ids:
            domain.append(('move_id.partner_category_id', 'in', self.partner_category_ids.ids))


        lines = self.env['account.move.line'].search(domain)

        # -------------------------------
        # جلب خطوط السنة اللي فاتت مرة واحدة
        # -------------------------------
        domain2 = [
            ('date', '>=', date_from_last_year),
            ('date', '<=', date_to_last_year),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_group', '=', 'income'),

        ]
        if self.product_ids:
            domain2.append(('product_id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            domain2.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
        if self.partner_ids:
            domain2.append(('move_id.partner_id', 'in', self.partner_ids.ids))
        if self.partner_category_ids:
            domain2.append(('move_id.partner_category_id', 'in', self.partner_category_ids.ids))

        last_year_lines = self.env['account.move.line'].search(domain2)



        # -------------------------------
        # Loop على المنتجات
        # -------------------------------
        for product in lines.mapped('product_id'):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code or ''

            partner_category_ids = False
            if self.groub_by_partner == 'partners':
                partner_category_ids = product_lines.mapped('move_id.partner_id')
            else:
                partner_category_ids = product_lines.mapped('move_id.partner_category_id')

            for partner in partner_category_ids:
                if self.groub_by_partner == 'partners':
                    current_lines = product_lines.filtered(lambda l: l.move_id.partner_id == partner)
                    last_year_partner_lines = last_year_lines.filtered(
                        lambda l: l.product_id == product and l.move_id.partner_id == partner)
                else:
                    current_lines = product_lines.filtered(lambda l: l.move_id.partner_category_id == partner)
                    last_year_partner_lines = last_year_lines.filtered(
                        lambda l: l.product_id == product and l.move_id.partner_category_id == partner)

                # -------- المبيعات الحالية --------
                qty_out_invoice = sum(current_lines.filtered(
                    lambda l: l.move_id.move_type == 'out_invoice' ).mapped(
                    'quantity'))
                qty_out_refund = sum(current_lines.filtered(
                    lambda l: l.move_id.move_type == 'out_refund' ).mapped(
                    'quantity'))
                total_quantity = qty_out_invoice - qty_out_refund

                price_out_invoice = sum(current_lines.filtered(
                    lambda l: l.move_id.move_type == 'out_invoice' ).mapped(
                    'price_subtotal'))
                price_out_refund = sum(current_lines.filtered(
                    lambda l: l.move_id.move_type == 'out_refund' ).mapped(
                    'price_subtotal'))
                total_price = price_out_invoice - price_out_refund

                nsap = total_price / total_quantity if total_quantity else 0.0

                # -------- السنة اللي فاتت --------
                last_qty_out_invoice = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
                last_qty_out_refund = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped('quantity'))
                last_year_total_quantity = last_qty_out_invoice - last_qty_out_refund

                last_price_out_invoice = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped(
                        'price_subtotal'))
                last_price_out_refund = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'out_refund').mapped(
                        'price_subtotal'))
                last_year_total_price = last_price_out_invoice - last_price_out_refund

                last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0

                # -------- المشتريات الحالية --------
                qty_in_invoice = sum(
                    current_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
                qty_in_refund = sum(
                    current_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
                total_quantity_invoice = qty_in_invoice - qty_in_refund

                price_in_invoice = sum(
                    current_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
                price_in_refund = sum(
                    current_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
                total_price_invoice = price_in_invoice - price_in_refund

                # naap = total_price_invoice / total_quantity_invoice if total_quantity_invoice else 0.0
                naap = product.standard_price
                # -------- السنة اللي فاتت مشتريات --------
                last_qty_in_invoice = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
                last_qty_in_refund = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
                last_year_total_quantity_invoice = last_qty_in_invoice - last_qty_in_refund

                last_price_in_invoice = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped(
                        'price_subtotal'))
                last_price_in_refund = sum(
                    last_year_partner_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped(
                        'price_subtotal'))
                last_year_total_price_invoice = last_price_in_invoice - last_price_in_refund

                # last_year_naap = last_year_total_price_invoice / last_year_total_quantity_invoice if last_year_total_quantity_invoice else 0.0
                last_year_naap = product.standard_price

                # -------- الحسابات النهائية --------
                margin = nsap - naap
                profit_value = margin * total_quantity
                last_margin = last_year_nsap - last_year_naap
                last_profit_value = last_margin * last_year_total_quantity

                # -------- Append --------
                combined_data.append({
                    'Product Category ID': product.categ_id.product_category,
                    'Product Order': product.product_category,

                    'Partner': partner.name if partner else '',
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
            combined_data = sorted(
                combined_data,
                key=lambda x: (
                    x['Product Category ID'] or 999999,
                    x['Product Order'] or 999999
                )
            )

        return {'combined_data': combined_data}


    def action_print_report_html(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('profit_report.report_action_profit_report_html').report_action(self, data=data)


    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_data': self.get_report_data()['combined_data'],
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
