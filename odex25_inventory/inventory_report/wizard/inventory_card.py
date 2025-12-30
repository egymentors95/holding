# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InventoryCard(models.TransientModel):
    _name = 'inventory.card'
    _description = 'Inventory Card'

    product_ids = fields.Many2many(
        'product.product',
        string='Products'
    )
    product_category_ids = fields.Many2many(
        'product.category',
        string='Product Categories'
    )
    location = fields.Many2one(comodel_name='stock.location', string='Location')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    # --------------------------------------------------
    # Initial Balance (رصيد قبل الفترة)
    # --------------------------------------------------
    def _get_initial_balance(self, product):
        domain = [
            ('state', '=', 'done'),
            ('product_id', '=', product.id),
            ('date', '<', self.date_from),
            ('company_id', 'in', self.env.companies.ids),
        ]
        if self.location:
            domain.append(('location_id', 'in', self.location.id))

        lines = self.env['stock.move.line'].search(domain)

        balance = 0.0
        for line in lines:
            if line.location_dest_id.usage == 'internal':
                balance += line.qty_done
            if line.location_id.usage == 'internal':
                balance -= line.qty_done

        return balance

    # --------------------------------------------------
    # Main Data Builder
    # --------------------------------------------------
    def get_report_data(self):
        combined_data = []

        if self.date_from > self.date_to:
            raise UserError(_("Date From must be before Date To."))

        # -----------------------------------
        # Products Scope
        # -----------------------------------
        product_domain = []
        if self.product_ids:
            product_domain.append(('id', 'in', self.product_ids.ids))
        if self.product_category_ids:
            product_domain.append(('categ_id', 'in', self.product_category_ids.ids))

        products = self.env['product.product'].search(product_domain)

        # -----------------------------------
        # Move Lines (Period)
        # -----------------------------------
        move_domain = [
            ('state', '=', 'done'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', 'in', self.env.companies.ids),
            ('product_id', 'in', products.ids),
        ]

        move_lines = self.env['stock.move.line'].search(
            move_domain, order='product_id, date, id'
        )

        balances = {}

        for line in move_lines:
            product = line.product_id

            # Initial Balance per product
            if product.id not in balances:
                balances[product.id] = self._get_initial_balance(product)

            qty_in = line.qty_done if line.location_dest_id.usage == 'internal' else 0
            qty_out = line.qty_done if line.location_id.usage == 'internal' else 0

            qty_before = balances[product.id]
            qty_after = qty_before + qty_in - qty_out
            balances[product.id] = qty_after

            avg_cost = product.standard_price
            total_cost = qty_after * avg_cost

            combined_data.append({
                'date': line.date,
                'product': product.display_name,
                'category': product.categ_id.display_name,
                'picking_type': line.picking_id.picking_type_id.name if line.picking_id else '',
                'qty_in': qty_in,
                'qty_out': qty_out,
                'qty_before': qty_before,
                'qty_after': qty_after,
                'avg_cost': avg_cost,
                'total_cost': total_cost,
            })

        return {'combined_data': combined_data}

    # --------------------------------------------------
    # XLSX Action
    # --------------------------------------------------
    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'lines': self.get_report_data()['combined_data'],
        }
        return self.env.ref(
            'inventory_report.report_action_inventory_card'
        ).report_action(self, data=data)

    def action_print_report_pdf(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'lines': self.get_report_data()['combined_data'],
        }
        return self.env.ref(
            'inventory_report.report_action_inventory_card_pdf'
        ).report_action(self, data=data)
