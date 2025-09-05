# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    sign_signature = fields.Binary(string="Digital Signature", )
    sign_initials = fields.Binary(string="Digitial Initials",)


    def __init__(self, pool, cr):
        """Custom initialization of the model"""
        super(ResUsers, self).__init__(pool, cr)

        # Dynamically add fields to SELF_WRITEABLE_FIELDS and SELF_READABLE_FIELDS
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS) + ['sign_signature', 'sign_initials']
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS) + ['sign_signature', 'sign_initials']
