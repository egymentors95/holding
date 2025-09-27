# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class InventoryReportWizard(models.TransientModel):
    _name = 'inventory.report.wizard'
    _description = 'Inventory Report'

    product_ids = fields.Many2many(string='Products', comodel_name='product.product')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    product_category_ids = fields.Many2many(string='Product Categories', comodel_name='product.category')
    lot_ids = fields.Many2many(string='Serial Number', comodel_name='stock.production.lot')

    def get_report_data(self):
        combined_data = []

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("Date From must be before or equal to Date To."))

        # -----------------------------------
        # 1- مبيعات الفترة (stock.move.line)
        # -----------------------------------
        domain_sales_period = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('state', '=', 'done'),
            ('picking_id.picking_type_code', '=', 'outgoing'),
        ]
        if self.product_ids:
            domain_sales_period.append(('product_id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            domain_sales_period.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
        if self.lot_ids:
            domain_sales_period.append(('lot_id', 'in', self.lot_ids.ids))

        sales_lines_period = self.env['stock.move.line'].search(domain_sales_period)

        # -----------------------------------
        # 2- مبيعات آخر 6 شهور
        # -----------------------------------
        if self.date_from:
            last_6_months_start = self.date_from - relativedelta(months=6)
            last_6_months_end = self.date_from - relativedelta(days=1)

            domain_sales_6m = [
                ('date', '>=', last_6_months_start),
                ('date', '<=', last_6_months_end),
                ('company_id', 'in', self.env.companies.ids),
                ('state', '=', 'done'),
                ('picking_id.picking_type_code', '=', 'outgoing'),
            ]
            if self.product_ids:
                domain_sales_6m.append(('product_id', 'in', self.product_ids.ids))
            if self.product_category_ids:
                domain_sales_6m.append(('product_id.categ_id', 'in', self.product_category_ids.ids))
            if self.lot_ids:
                domain_sales_6m.append(('lot_id', 'in', self.lot_ids.ids))

            sales_lines_6m = self.env['stock.move.line'].search(domain_sales_6m)
        else:
            sales_lines_6m = self.env['stock.move.line']

        # -----------------------------------
        # 3- المشتريات (account.move.line)
        # -----------------------------------
        domain_purchases = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('move_id.state', '=', 'posted'),
        ]
        if self.product_ids:
            domain_purchases.append(('product_id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            domain_purchases.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        purchase_lines = self.env['account.move.line'].search(domain_purchases)

        # -----------------------------------
        # 4- تجميع كل المنتجات
        # -----------------------------------
        all_products = (sales_lines_period.mapped("product_id") |
                        sales_lines_6m.mapped("product_id") |
                        purchase_lines.mapped("product_id"))

        # -----------------------------------
        # 5- لوب واحد لكل منتج
        # -----------------------------------
        for product in all_products:
            # مبيعات الفترة
            period_lines = sales_lines_period.filtered(lambda l: l.product_id == product)
            move_qty = sum(period_lines.mapped("qty_done"))

            # مبيعات آخر 6 شهور
            sales_6m_lines = sales_lines_6m.filtered(lambda l: l.product_id == product)
            sold_last_6_months = sum(sales_6m_lines.mapped("qty_done"))
            avg_sold_last_6_months = sold_last_6_months / 6 if sold_last_6_months else 0
            on_hand_qty = product.qty_available
            equ_month = on_hand_qty / avg_sold_last_6_months if avg_sold_last_6_months else 0


            # المشتريات
            purchase_product_lines = purchase_lines.filtered(lambda l: l.product_id == product)
            qty_in_invoice = sum(
                purchase_product_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('quantity'))
            qty_in_refund = sum(
                purchase_product_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('quantity'))
            total_quantity_invoice = qty_in_invoice - qty_in_refund

            price_in_invoice = sum(
                purchase_product_lines.filtered(lambda l: l.move_id.move_type == 'in_invoice').mapped('price_subtotal'))
            price_in_refund = sum(
                purchase_product_lines.filtered(lambda l: l.move_id.move_type == 'in_refund').mapped('price_subtotal'))
            total_price_invoice = price_in_invoice - price_in_refund

            naap = total_price_invoice / total_quantity_invoice if total_quantity_invoice else 0.0
            value = naap * on_hand_qty

            combined_data.append({
                'Product': product.name,
                'Default Code': product.default_code or '',
                'Product Category': product.categ_id.name,

                'Lots': ", ".join(period_lines.mapped("lot_id.name")),
                'on_hand_qty': product.qty_available,  # الكمية الحالية
                'move_qty': move_qty,  # مبيعات الفترة
                'sold_last_6_months': sold_last_6_months,  # مبيعات 6 شهور
                'avg_sold_last_6_months': avg_sold_last_6_months,  # المتوسط الشهري
                'equ_month': equ_month,  # يغطي كام شهر
                'purchased_qty': total_quantity_invoice,  # الكمية المشتراة
                'purchased_value': total_price_invoice,  # قيمة المشتريات
                'naap': naap,  # متوسط الشراء
                'value': value,
            })

        return {'combined_data': combined_data}

    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('inventory_report.report_action_inventory_report').report_action(self, data=data)

    def action_print_report_html(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.get_report_data()['combined_data'],
        }
        return self.env.ref('inventory_report.report_action_inventory_report_html').report_action(self, data=data)

    def action_view_report(self):
        self.ensure_one()
        report_data = self.get_report_data()['combined_data']

        self.env['stock.views'].search([]).unlink()

        for rec in report_data:
            self.env['stock.views'].create({
                'product_category': rec['Product Category'],
                'product_name': rec['Product'],
                'default_code': rec['Default Code'],
                'Lots': rec['Lots'],
                'on_hand_qty': rec['on_hand_qty'],
                'sold_last_6_months': rec['sold_last_6_months'],
                'avg_sold_last_6_months': rec['avg_sold_last_6_months'],
                'equ_month': rec['equ_month'],
                'naap': rec['naap'],
                'value': rec['value'],

            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Views',
            'res_model': 'stock.views',
            'view_mode': 'tree',
            'target': 'current',
        }
