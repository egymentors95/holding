from odoo import models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # أولاً نكمل الـ validation الطبيعي
        res = super().button_validate()

        print(">>> PICKING DONE <<<", self.name)

        # نمر على كل move في الاستلام
        for move in self.move_lines:
            if move.product_id.valuation != 'real_time':
                continue  # بس للـ real_time

            # ناخد الـ SVL اللي اتعمل بعد action_done
            svls = move.stock_valuation_layer_ids
            if not svls:
                print(f">>> NO SVL CREATED FOR MOVE {move.id}")
                continue

            for svl in svls:
                try:
                    # نحضر الحسابات والجورنال
                    journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
                    qty = svl.quantity
                    cost = svl.value
                    description = svl.description or move.name

                    # نختار الحسابات حسب اتجاه الحركة
                    if move._is_in():
                        debit_account_id = acc_dest
                        credit_account_id = acc_valuation
                    else:
                        debit_account_id = acc_valuation
                        credit_account_id = acc_src

                    # نعمل entry
                    move._create_account_move_line(
                        credit_account_id=credit_account_id,
                        debit_account_id=debit_account_id,
                        journal_id=journal_id,
                        qty=qty,
                        description=description,
                        svl_id=svl.id,
                        cost=cost
                    )
                    print(f">>> ACCOUNT ENTRY CREATED FOR MOVE {move.id}")

                except UserError as e:
                    print(f">>> USER ERROR FOR MOVE {move.id}: {e}")
                except Exception as e:
                    print(f">>> ERROR FOR MOVE {move.id}: {e}")

        return res


class StockMoveDebug(models.Model):
    _inherit = 'stock.move'

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



