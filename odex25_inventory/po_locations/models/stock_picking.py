from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        for rec in self:
            if rec.location_dest_id:
                if rec.location_dest_id.user_id != self.env.user:
                    raise UserError(_(
                        "You are not allowed to validate this picking.\n"
                        "Only %s can validate it."
                    ) % rec.location_dest_id.user_id.name)

        return super(StockPicking, self).button_validate()

