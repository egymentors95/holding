from odoo import models, fields, api



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=True)



    @api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.invoice_user_id', 'move_id', 'move_id.invoice_line_ids')
    def _compute_analytic_account_id(self):
        for record in self:
            if record.move_id.invoice_user_id:
                record.analytic_account_id = record.move_id.invoice_user_id.analytic_account_id.id
            else:
                if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                    rec = self.env['account.analytic.default'].account_get(
                        product_id=record.product_id.id,
                        partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                        account_id=record.account_id.id,
                        user_id=record.env.uid,
                        date=record.date,
                        company_id=record.move_id.company_id.id
                    )
                    if rec:
                        record.analytic_account_id = rec.analytic_id