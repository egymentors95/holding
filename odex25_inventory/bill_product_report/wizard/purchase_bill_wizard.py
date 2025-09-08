# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class PurchaseBillWizard(models.TransientModel):
    _name = 'purchase.bill.wizard'
    _description = 'Wizard to Generate Vendor Bills Report'

    product_ids = fields.Many2many(string='Products', comodel_name='product.product')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    vendor_ids = fields.Many2many(string='Vendors', comodel_name='res.partner', domain="[('supplier_rank','>',0)]")
    product_category_ids = fields.Many2many(string='Product Categories', comodel_name='product.category')

    def get_report_data(self):
        combined_data = []

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError("Date From must be before or equal to Date To.")

        # فترات السنة اللي فاتت
        date_from_last_year = self.date_from - relativedelta(years=1) if self.date_from else False
        date_to_last_year = self.date_to - relativedelta(years=1) if self.date_to else False

        # -------------------------------
        # جلب كل خطوط الفواتير (Bills)
        # -------------------------------
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.vendor_ids:
            domain.append(('move_id.partner_id', 'in', self.vendor_ids.ids))
        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        lines = self.env['account.move.line'].search(domain)

        # -------------------------------
        # جلب خطوط السنة اللي فاتت (Bills)
        # -------------------------------
        last_year_lines = self.env['account.move.line'].search([
            ('date', '>=', date_from_last_year),
            ('date', '<=', date_to_last_year),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
        ])

        # -------------------------------
        # Loop على المنتجات
        # -------------------------------
        for product in lines.mapped('product_id'):
            product_lines = lines.filtered(lambda l: l.product_id == product)
            product_category = product.categ_id.name
            product_name = product.name
            default_code = product.default_code or ''

            # لو فيه أكتر من Vendor
            for vendor in product_lines.mapped('move_id.partner_id'):
                vendor_lines = product_lines.filtered(lambda l: l.move_id.partner_id == vendor)

                #------Plan Lines -------

                plan_lines = self.env['purchase.order.line'].search([
                    ('product_id', '=', product.id),
                    ('order_line.partner_id', '=', vendor.id),
                    ('order_line.plan_start_date', '<=', self.date_to),
                    ('order_line.plan_end_date', '>=', self.date_from),
                    ('order_line.state', '=', 'draft'),
                    # ('order_line.company_id', 'in', self.env.companies.ids),
                ])
                plan_qty = 0.0
                if self.date_from and self.date_to:
                    current = self.date_from.replace(day=1)
                    end = self.date_to.replace(day=1)

                    months = []
                    while current <= end:
                        months.append(current.strftime("%B").lower())
                        current += relativedelta(months=1)

                    for plan in plan_lines:
                        for month in months:
                            if hasattr(plan, month):
                                plan_qty += getattr(plan, month) or 0.0
                value = plan_qty * plan_lines.price_unit if plan_lines else 0.0



                # -------- المشتريات الحالية --------
                qty_in_invoice = sum(vendor_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
                qty_in_refund = sum(vendor_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
                total_quantity = qty_in_invoice - qty_in_refund
                achive = total_quantity / plan_qty * 100 if plan_qty else 0.0

                price_in_invoice = sum(vendor_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
                price_in_refund = sum(vendor_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
                total_price = price_in_invoice - price_in_refund

                nsap = total_price / total_quantity if total_quantity else 0.0

                # -------- السنة اللي فاتت --------
                last_year_purchases = last_year_lines.filtered(lambda l: l.product_id == product and l.move_id.partner_id == vendor)

                last_qty_in_invoice = sum(last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
                last_qty_in_refund = sum(last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
                last_year_total_quantity = last_qty_in_invoice - last_qty_in_refund

                last_price_in_invoice = sum(last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
                last_price_in_refund = sum(last_year_purchases.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
                last_year_total_price = last_price_in_invoice - last_price_in_refund

                last_year_nsap = last_year_total_price / last_year_total_quantity if last_year_total_quantity else 0.0

                # -------- Append --------
                combined_data.append({
                    'Product Category': product_category,
                    'Product': product_name,
                    'Default Code': default_code,
                    'Vendor': vendor.name,
                    'Vendor id': vendor.id,

                    'Total Quantity': total_quantity,
                    'Total Price': total_price,
                    'Nsap': nsap,

                    # 'Last Year Total Quantity': last_year_total_quantity,
                    # 'Last Year Total Price': last_year_total_price,
                    # 'Last Year Nsap': last_year_nsap,

                    'Plan Quantity': plan_qty,
                    'Plan Value': value,
                    'Achive': achive,
                })

        return {'combined_data': combined_data}


    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('bill_product_report.report_action_invoice_bill').report_action(self, data=data)


    def action_view_report(self):
        self.ensure_one()
        report_data = self.get_report_data()['combined_data']

        self.env['account.move.line3'].search([]).unlink()

        for rec in report_data:
            self.env['account.move.line3'].create({
                'product_category': rec['Product Category'],
                'product_name': rec['Product'],
                'default_code': rec['Default Code'],
                'vendor_id': rec['Vendor id'],

                # 'last_total_quantity': rec['Last Year Total Quantity'],
                # 'last_total_price': rec['Last Year Total Price'],
                # 'last_nsap': rec['Last Year Nsap'],

                'total_quantity': rec['Total Quantity'],
                'total_price': rec['Total Price'],
                'nsap': rec['Nsap'],

                'plan_quantity': rec['Plan Quantity'],
                'plan_value': rec['Plan Value'],
                'achive': rec['Achive'],
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills Data',
            'res_model': 'account.move.line3',
            'view_mode': 'tree',
            'target': 'current',
        }
