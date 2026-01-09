from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_invoice_direct(self):
        """يستدعي الـ wizard sale.advance.payment.inv وينفذ إنشاء الفاتورة"""
        for order in self:
            # إنشاء الـ wizard من الموديل SaleAdvancePaymentInv
            wizard = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'delivered',  # أو 'all' لو عايز لكل الطلب
            })

            # تمرير الـ sale.order الحالي في الـ context
            ctx = {
                'active_model': 'sale.order',
                'active_ids': [order.id],
                'active_id': order.id,
                'open_invoices': False,  # لو عايز تفتح الفاتورة بعد الإنشاء خليها True
            }

            # استدعاء دالة الإنشاء من الـ wizard
            wizard.with_context(ctx).create_invoices()

        return True


