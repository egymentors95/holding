from odoo import models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # 1️⃣ نفذ الـ validation الطبيعي
        res = super().button_validate()

        for picking in self:
            print("\n>>> PICKING DONE <<<", picking.name)

            for move in picking.move_lines:

                # فقط المنتجات ذات real_time valuation
                if move.product_id.valuation != 'real_time':
                    continue

                # منع التكرار
                if move.account_move_ids:
                    print(">>> MOVE ALREADY POSTED:", move.id)
                    continue

                # لازم يكون في SVL
                svls = move.stock_valuation_layer_ids
                if not svls:
                    print(">>> NO SVL FOR MOVE:", move.id)
                    continue

                for svl in svls:
                    try:
                        # 2️⃣ الحسابات والجورنال
                        journal_id, acc_src, acc_dest, acc_valuation = \
                            move._get_accounting_data_for_valuation()

                        qty = abs(svl.quantity)
                        cost = abs(svl.value)
                        description = svl.description or move.name

                        src_usage = move.location_id.usage
                        dest_usage = move.location_dest_id.usage

                        print("\n--- MOVE DEBUG ---")
                        print("MOVE:", move.id)
                        print("SRC:", move.location_id.display_name, src_usage)
                        print("DST:", move.location_dest_id.display_name, dest_usage)
                        print("QTY:", qty, "COST:", cost)

                        # 3️⃣ تحديد الاتجاه الصحيح
                        if src_usage == 'supplier' and dest_usage == 'internal':
                            # 📥 Receipt
                            debit_account_id = acc_dest  # Stock Input
                            credit_account_id = acc_valuation  # Stock Valuation

                        elif src_usage == 'internal' and dest_usage in ('customer', 'supplier'):
                            # 📤 Delivery
                            debit_account_id = acc_valuation  # Stock Valuation
                            credit_account_id = acc_src  # Stock Output

                        else:
                            print(">>> SKIPPED MOVE (NO VALUATION FLOW)")
                            continue

                        # 4️⃣ إنشاء القيد
                        move._create_account_move_line(
                            credit_account_id=credit_account_id,
                            debit_account_id=debit_account_id,
                            journal_id=journal_id,
                            qty=qty,
                            description=description,
                            svl_id=svl.id,
                            cost=cost
                        )

                        print(">>> ACCOUNT ENTRY CREATED FOR MOVE:", move.id)

                    except UserError as e:
                        print(">>> USER ERROR:", e)
                    except Exception as e:
                        print(">>> SYSTEM ERROR:", e)

        return res


# class StockMoveDebug(models.Model):
#     _inherit = 'stock.move'

    # def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
    #                               cost):
    #     self.ensure_one()
    #     AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
    #
    #     move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
    #
    #     print(">>> DEBUG ACCOUNT MOVE CREATION")
    #     print("MOVE ID:", self.id)
    #     print("PRODUCT:", self.product_id.display_name)
    #     print("QTY:", qty)
    #     print("COST:", cost)
    #     print("JOURNAL ID:", journal_id)
    #     print("DEBIT ACCOUNT:", debit_account_id)
    #     print("CREDIT ACCOUNT:", credit_account_id)
    #     print("LINE IDS:", move_lines)
    #     print("SVL ID:", svl_id)
    #
    #     if move_lines:
    #         date = self._context.get('force_period_date', fields.Date.context_today(self))
    #         new_account_move = AccountMove.sudo().create({
    #             'line_ids': move_lines,
    #             'date': date,
    #             'ref': self.name,
    #             'stock_move_id': self.id,
    #             'stock_valuation_layer_ids': [(6, 0, [svl_id])] if svl_id else False,
    #             'move_type': 'entry',
    #         })
    #         print(">>> ACCOUNT MOVE CREATED ID:", new_account_move.id)
    #         new_account_move.sudo()._post()
    #         print(">>> ACCOUNT MOVE POSTED")



