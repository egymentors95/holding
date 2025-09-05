import base64
import re
from odoo import models, fields, api, exceptions, tools, _
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning, ValidationError
from odoo.modules.module import get_module_resource
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    identification_type = fields.Selection([('id', 'National ID'),
                                            ('iqama', 'Iqama'),
                                            ('passport', 'Passport'),
                                            ('other', 'Other')], default='id',string='Identification Type')
    identification_number = fields.Char(string='Identification NUmber',copy=False)
    identification_issue_date = fields.Date(string='Identification Issue Date')
    identification_expiry_date = fields.Date(string='Identification Expiry Date',copy=False)
    issuer = fields.Char(string='Issuer')
    copy_no = fields.Integer(string='Copy No')

    @api.constrains('identification_expiry_date', 'identification_type', 'identification_number', 'identification_issue_date')
    def check_expr_date(self):
        for each in self:
            if each.identification_expiry_date:
                 exp_date = fields.Date.from_string(each.identification_expiry_date)
                 if exp_date < date.today():
                     raise Warning(_('Your Document Is Expired.'))

            if each.identification_type == 'id':
                if each.identification_number and len(each.identification_number) != 10:
                    raise Warning(_('Saudi ID must be 10 digits'))
                if each.identification_number and each.identification_number[0] != '1':
                    raise Warning(_('The Saudi ID number should begin with 1'))

            if each.identification_type == 'iqama':
                if each.identification_number and len(each.identification_number) != 10:
                    raise Warning(_('Identity must be 10 digits'))
                if each.identification_number and each.identification_number[0] not in ['2', '3', '4']:
                    raise Warning(_('Identity must begin with 2 or 3 or 4'))

            if each.identification_expiry_date and each.identification_issue_date:
                if each.identification_expiry_date <= each.identification_issue_date:
                    raise Warning(_('Error, date of issue must be less than expiry date'))

                if date.today() >= each.identification_expiry_date:
                    raise Warning(_("Error, the expiry date must be greater than the date of the day"))

    # @api.constrains('mobile')
    # def _check_phone_length_and_digits(self):
    #     for record in self:
    #         if record.mobile:
    #             if not record.mobile.isdigit() or len(record.mobile) != 10:
    #                 raise ValidationError(_("The mobile number must contain exactly 10 digits and no letters or symbols."))


    @api.constrains('email')
    def _check_email_format(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(_("Invalid email address."))