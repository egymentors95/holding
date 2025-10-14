# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'Sales Partner report'

    product_ids = fields.Many2many(string='Products', comodel_name='product.product')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    product_category_ids = fields.Many2many(string='Product Categories', comodel_name='product.category')
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
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.partner_ids:
            domain.append(('move_id.partner_id', 'in', self.partner_ids.ids))
        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
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
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        if self.product_ids:
            domain2.append(('product_id', 'in', self.product_ids.ids))
        if self.partner_ids:
            domain2.append(('move_id.partner_id', 'in', self.partner_ids.ids))
        if self.product_category_ids:
            domain2.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
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
                partner_lines = False
                if self.groub_by_partner == 'partners':
                    partner_lines = product_lines.filtered(lambda l: l.move_id.partner_id == partner)
                else:
                    partner_lines = product_lines.filtered(lambda l: l.move_id.partner_category_id == partner)





                # -------- خطط المبيعات --------
                number_of_months = 0
                if self.date_from and self.date_to:
                    diff = relativedelta(self.date_to, self.date_from)
                    number_of_months = diff.years * 12 + diff.months + 1


                # -------- المبيعات الحالية --------
                qty_out_invoice = sum(partner_lines.filtered(lambda
                                                               l: l.move_id.move_type == 'out_invoice').mapped(
                    'quantity'))
                qty_out_refund = sum(partner_lines.filtered(lambda
                                                              l: l.move_id.move_type == 'out_refund').mapped(
                    'quantity'))
                total_quantity = qty_out_invoice - qty_out_refund

                price_out_invoice = sum(partner_lines.filtered(lambda
                                                                 l: l.move_id.move_type == 'out_invoice').mapped(
                    'price_subtotal'))
                price_out_refund = sum(partner_lines.filtered(lambda
                                                                l: l.move_id.move_type == 'out_refund').mapped(
                    'price_subtotal'))
                total_price = price_out_invoice - price_out_refund

                nsap = total_price / total_quantity if total_quantity else 0.0


                # -------- السنة اللي فاتت --------
                last_year_sales = last_year_lines.filtered(
                    lambda l: l.product_id == product and
                              l.move_id.partner_id == partner)

                last_qty_out_invoice = sum(
                    last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice').mapped('quantity'))
                last_qty_out_refund = sum(
                    last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund' ).mapped('quantity'))
                last_year_total_quantity = last_qty_out_invoice - last_qty_out_refund

                last_price_out_invoice = sum(
                    last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_invoice' ).mapped(
                        'price_subtotal'))
                last_price_out_refund = sum(
                    last_year_sales.filtered(lambda l: l.move_id.move_type == 'out_refund' ).mapped(
                        'price_subtotal'))
                last_year_total_price = last_price_out_invoice - last_price_out_refund

                last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0


                # -------- Append --------
                combined_data.append({
                    'Product Category ID': product.categ_id.product_category,
                    'Product Order': product.product_category,

                    'Product Category': product_category,
                    'Product': product_name,
                    'Default Code': default_code,
                    'Partner': partner.name,
                    'Partner id': partner.id,
                    'Partner Category': partner.name if self.groub_by_partner == 'category' else (
                        partner.category_id.name if hasattr(partner, 'category_id') else ''),

                    'Total Quantity': total_quantity,
                    'Total Price': total_price,
                    'Nsap': nsap,

                    'Last Year Total Quantity': last_year_total_quantity,
                    'Last Year Total Price': last_year_total_price,
                    'Last Year Nsap': last_year_nsap,

                })
            combined_data = sorted(
                combined_data,
                key=lambda x: (
                    x['Product Category ID'] or 999999,
                    x['Product Order'] or 999999
                )
            )

        return {'combined_data': combined_data}

    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        ctx = dict(self.env.context)
        ctx['group_mode'] = self.groub_by_partner
        return self.env.ref('sales_partner_report.report_action_sales_partner').with_context(ctx).report_action(self,
                                                                                                                data=data)

    def action_print_report_html(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('sales_partner_report.report_action_sales_partner_html').report_action(self, data=data)


