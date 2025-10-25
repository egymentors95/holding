from odoo import models, fields

class TotalTaxReport(models.TransientModel):
    _name = 'total.tax.report'
    _description = 'Taxes Report Wizard'

    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    def get_data(self):
        AccountMoveLine = self.env['account.move.line']
        date_start, date_end = self.date_start, self.date_end

        def sum_credit(lines): return sum(lines.mapped('credit'))
        def sum_debit(lines): return sum(lines.mapped('debit'))

        # ============= المبيعات 15% =============
        domain_sales_15 = [
            ('date', '>=', date_start), ('date', '<=', date_end),
            ('parent_state', '=', 'posted'),
            ('tax_ids.amount', '=', 15),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        lines_15 = AccountMoveLine.search(domain_sales_15)

        sales_lines_15 = lines_15.filtered(lambda l: l.move_id.move_type == 'out_invoice')
        refund_lines_15 = lines_15.filtered(lambda l: l.move_id.move_type == 'out_refund')

        total_sales_untaxed_15 = abs(sum_credit(sales_lines_15) - sum_debit(sales_lines_15)) / 1.15
        total_refund_untaxed_15 = abs(sum_debit(refund_lines_15) - sum_credit(refund_lines_15)) / 1.15
        vat_sales_15 = (total_sales_untaxed_15 - total_refund_untaxed_15) * 0.15

        # ============= المبيعات 0% =============
        domain_sales_0 = [
            ('date', '>=', date_start), ('date', '<=', date_end),
            ('parent_state', '=', 'posted'),
            ('tax_ids.amount', '=', 0),
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        lines_0 = AccountMoveLine.search(domain_sales_0)

        sales_lines_0 = lines_0.filtered(lambda l: l.move_id.move_type == 'out_invoice')
        refund_lines_0 = lines_0.filtered(lambda l: l.move_id.move_type == 'out_refund')

        total_sales_untaxed_0 = abs(sum_credit(sales_lines_0) - sum_debit(sales_lines_0))
        total_refund_untaxed_0 = abs(sum_debit(refund_lines_0) - sum_credit(refund_lines_0))
        vat_sales_0 = 0.0

        # ============= المشتريات 15% =============
        domain_purchase_15 = [
            ('date', '>=', date_start), ('date', '<=', date_end),
            ('parent_state', '=', 'posted'),
            ('tax_ids.amount', '=', 15),
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
        ]
        lines_purch_15 = AccountMoveLine.search(domain_purchase_15)

        purchase_lines_15 = lines_purch_15.filtered(lambda l: l.move_id.move_type == 'in_invoice')
        refund_purchase_lines_15 = lines_purch_15.filtered(lambda l: l.move_id.move_type == 'in_refund')

        total_purchase_untaxed_15 = abs(sum_debit(purchase_lines_15) - sum_credit(purchase_lines_15)) / 1.15
        total_refund_purchase_untaxed_15 = abs(sum_credit(refund_purchase_lines_15) - sum_debit(refund_purchase_lines_15)) / 1.15
        vat_purchase_15 = (total_purchase_untaxed_15 - total_refund_purchase_untaxed_15) * 0.15

        # ============= المشتريات 0% =============
        domain_purchase_0 = [
            ('date', '>=', date_start), ('date', '<=', date_end),
            ('parent_state', '=', 'posted'),
            ('tax_ids.amount', '=', 0),
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
        ]
        lines_purch_0 = AccountMoveLine.search(domain_purchase_0)

        purchase_lines_0 = lines_purch_0.filtered(lambda l: l.move_id.move_type == 'in_invoice')
        refund_purchase_lines_0 = lines_purch_0.filtered(lambda l: l.move_id.move_type == 'in_refund')

        total_purchase_untaxed_0 = abs(sum_debit(purchase_lines_0) - sum_credit(purchase_lines_0))
        total_refund_purchase_untaxed_0 = abs(sum_credit(refund_purchase_lines_0) - sum_debit(refund_purchase_lines_0))
        vat_purchase_0 = 0.0

        # ============= الإجماليات =============
        total_sales = total_sales_untaxed_15 + total_sales_untaxed_0
        total_sales_refund = total_refund_untaxed_15 + total_refund_untaxed_0
        total_sales_vat = vat_sales_15 + vat_sales_0

        total_purchases = total_purchase_untaxed_15 + total_purchase_untaxed_0
        total_purchases_refund = total_refund_purchase_untaxed_15 + total_refund_purchase_untaxed_0
        total_purchases_vat = vat_purchase_15 + vat_purchase_0

        result = [
            # ==== SALES ====
            {
                'description': 'المبيعات الخاضعة للنسبة الأساسية 15%',
                'price': round(total_sales_untaxed_15, 2),
                'refund': round(total_refund_untaxed_15, 2),
                'vat': round(vat_sales_15, 2),
            },
            {
                'description': 'مبيعات محلية خاضعة للنسبة الصفرية',
                'price': round(total_sales_untaxed_0, 2),
                'refund': round(total_refund_untaxed_0, 2),
                'vat': round(vat_sales_0, 2),
            },
            {
                'description': 'الإجمالي (المبيعات)',
                'price': round(total_sales, 2),
                'refund': round(total_sales_refund, 2),
                'vat': round(total_sales_vat, 2),
            },
            # ==== PURCHASES ====
            {
                'description': 'المشتريات الخاضعة للنسبة الأساسية 15%',
                'price': round(total_purchase_untaxed_15, 2),
                'refund': round(total_refund_purchase_untaxed_15, 2),
                'vat': round(vat_purchase_15, 2),
            },
            {
                'description': 'مشتريات محلية خاضعة للنسبة الصفرية',
                'price': round(total_purchase_untaxed_0, 2),
                'refund': round(total_refund_purchase_untaxed_0, 2),
                'vat': round(vat_purchase_0, 2),
            },
            {
                'description': 'الإجمالي (المشتريات)',
                'price': round(total_purchases, 2),
                'refund': round(total_purchases_refund, 2),
                'vat': round(total_purchases_vat, 2),
            },
        ]

        return result


    def action_print_report_xlsx(self):
        self.ensure_one()
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'lines': self.get_data(),
        }
        return self.env.ref('taxes_reports.report_action_total_tax').report_action(self, data=data)
