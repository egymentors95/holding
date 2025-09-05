# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_round
from collections import defaultdict

class HrExpense(models.Model):
    _inherit = "hr.expense"

    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead')


    def action_move_create(self):
        # Filter out refused expenses
        expenses = self.filtered(lambda x: not x.is_refused)
        
        # Group expenses by their respective sheets
        expenses_by_sheet = {}
        for expense in expenses:
            sheet = expense.sheet_id
            if sheet not in expenses_by_sheet:
                expenses_by_sheet[sheet] = self.env['hr.expense']
            expenses_by_sheet[sheet] += expense

        # Get moves and line values using the filtered expenses
        move_group_by_sheet = expenses._get_account_move_by_sheet()
        move_line_values_by_expense = expenses._get_account_move_line_values()

        # Process each expense sheet
        for sheet, sheet_expenses in expenses_by_sheet.items():
            move = move_group_by_sheet[sheet.id]

            # Collect all move line values for this sheet
            all_move_line_values = []
            for expense in sheet_expenses:
                all_move_line_values.extend(move_line_values_by_expense.get(expense.id, []))

            # Consolidate lines by account_id
            grouped_lines = defaultdict(lambda: {'debit': 0.0, 'credit': 0.0, 'values': {}})
            for line in all_move_line_values:
                account_id = line['account_id']
                grouped_lines[account_id]['debit'] += line.get('debit', 0.0)
                grouped_lines[account_id]['credit'] += line.get('credit', 0.0)
                if not grouped_lines[account_id]['values']:
                    grouped_lines[account_id]['values'] = {
                        k: v for k, v in line.items() if k not in ('debit', 'credit')
                    }

            # Prepare final move lines with consolidated values
            final_move_lines = []
            for account_group in grouped_lines.values():
                line_data = account_group['values'].copy()
                line_data['debit'] = float_round(account_group['debit'], precision_digits=2)
                line_data['credit'] = float_round(account_group['credit'], precision_digits=2)
                final_move_lines.append((0, 0, line_data))

            # Update the move with new lines (clear existing first)
            move.write({'line_ids': [(5, 0, 0)] + final_move_lines})

            # Link the move to the expense sheet
            sheet.write({'account_move_id': move.id})

            # Mark as paid if all expenses are company-paid
            if all(expense.payment_mode == 'company_account' for expense in sheet_expenses):
                sheet.paid_expense_sheets()

        # Post all generated accounting moves
        for move in move_group_by_sheet.values():
            move._post()

        return move_group_by_sheet

    
