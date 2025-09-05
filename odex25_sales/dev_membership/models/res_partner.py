# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models, api,_
from datetime import datetime

from odoo.exceptions import Warning, ValidationError
import re
import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    is_member = fields.Boolean(string='Is Member' ,default=False)
    mobile = fields.Char(copy=False)
    identification_number = fields.Char(copy=False)
    
    membership_count = fields.Integer(string="Membership Count", compute="_get_membership_count")
    active_membership_id = fields.Many2one('dev.membership', string='Membership', compute='check_active_membership')
    membrship_level = fields.Many2one('membership.level',string='Membrship level',store=True,compute='_compute_membership_level')
    nationality_id = fields.Many2one('res.country', string="Nationality",default=lambda self: self.env.user.company_id.country_id)
    is_membership_expire = fields.Boolean('Expire Membership',store=True, compute='check_active_membership')
    memebership_status = fields.Char('Membership Status',store=True,compute='check_memebership_status')
    membrship_no = fields.Char('Membership Number')
    birth_date  = fields.Date(string='Birth Date')
    join_date  = fields.Date(string='Join Date')
    memebership_end_date  = fields.Date(string='Memebership End Date',store=True, compute='check_active_membership')
    age = fields.Integer(string='Age',compute='_compute_age')
    employer  = fields.Char(string='Employer',)
    product_id = fields.Many2one('product.product', string="Membership Type",store=True,compute="check_active_membership")
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female")], default="male",string='Gender'
    )
    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            rec.age = 0
            if rec.birth_date:
                rec.age = (datetime.today().year-rec.birth_date.year)


    def check_active_membership(self):
        for partner in self:
            partner.active_membership_id = False
            partner.is_membership_expire = False
            partner.memebership_end_date = False
            partner.product_id = False
            if partner.membership_count > 0:
                c_date = datetime.now().date()
                membership_id = self.env['dev.membership'].sudo().search([('partner_id', '=', partner.id),('state', '=', 'active'),('from_date', '<=', c_date), ('to_date', '>=', c_date)], order='to_date desc', limit=1)
                if membership_id:
                    partner.active_membership_id = membership_id and membership_id.id or False
                    last_membership_id = self.env['dev.membership'].sudo().search([
                        ('partner_id', '=', partner.id),
                        ('state', '=', 'active'),
                        ('product_id', '=', membership_id.product_id.id)], order='to_date desc', limit=1)
                    if last_membership_id:
                        partner.memebership_end_date = last_membership_id.to_date
                        partner.product_id = last_membership_id.product_id.id
                else:
                    partner.is_membership_expire = True
                    last_membership_id = self.env['dev.membership'].sudo().search([('partner_id', '=', partner.id),('state', 'in', ('expire', 'cancel'))], order='to_date desc', limit=1)
                    if last_membership_id:
                        partner.memebership_end_date = last_membership_id.to_date
                        partner.product_id = last_membership_id.product_id.id
    @api.depends('active_membership_id')
    def _compute_membership_end(self):
      for partner in self:
        partner.membership_end_date = False
        if partner.membership_count > 0:
            if partner.active_membership_id:
                # Search for the latest active membership with the same product
                membership = self.env['dev.membership'].sudo().search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'active'),
                    ('product_id', '=', partner.active_membership_id.product_id.id)
                ], order='to_date desc', limit=1)
                if membership:
                    partner.membership_end_date = membership.to_date
            else:
                # Find the latest expired or cancelled membership
                membership = self.env['dev.membership'].sudo().search([
                    ('partner_id', '=', partner.id),
                    ('state', 'in', ('expire', 'cancel'))
                ], order='to_date desc', limit=1)
                if membership:
                    partner.membership_end_date = membership.to_date
                    
    @api.depends('active_membership_id')             
    def _compute_membership_level(self):
        for partner in self:
            partner.membrship_level = False
            if partner.membership_count > 0:
                membership_id = self.env['dev.membership'].sudo().search([
                	    ('partner_id', '=', partner.id),
                	    ('state', 'in', ('active','expire','cancel'))], order='to_date desc', limit=1)
                if membership_id:
                        partner.membrship_level = membership_id.membrship_level

    @api.depends('active_membership_id')
    def check_memebership_status(self):
        for partner in self:
            partner.memebership_status = ''
            if partner.membership_count == 0:
                partner.memebership_status = (_('No Membership'))
            else:
                if partner.active_membership_id:
                    partner.memebership_status = partner.active_membership_id.product_id.name
                else:
                    last_membership = self.env['dev.membership'].search(
                        [('partner_id', '=', partner.id)], order='to_date desc', limit=1)

                    if last_membership:
                        if last_membership.state == 'draft':
                            partner.memebership_status = (_('Membership Waiting'))
                        elif last_membership.state == 'cancel':
                            partner.memebership_status = (_('Membership Cancelled'))
                        elif last_membership.state == 'confirm':
                            if not last_membership.invoice_id and not last_membership.is_free:
                                partner.memebership_status = (_('Membership Waiting for Invoice'))
                            elif last_membership.invoice_id.payment_state in ['paid', 'in_payment']:
                                partner.memebership_status = (_('Membership Paid'))
                            elif last_membership.invoice_id.payment_state not in ['paid', 'in_payment']:
                                partner.memebership_status = (_('Membership Waiting for Payment'))
                    # If no active or draft memberships exist, check for expiration
                    if not partner.memebership_status and partner.is_membership_expire:
                        partner.memebership_status = (_('Membership Expire'))


    
    def _get_membership_count(self):
        for rec in self:
            membership_count = self.env['dev.membership'].search_count([('partner_id', '=', rec.id)])
            rec.membership_count = membership_count

    def view_membership(self):
        ctx = dict(create=False, search_default_state=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Membership',
            'res_model': 'dev.membership',
            'domain': [('partner_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': ctx,
        }

    def get_board_nominations(self):
        nominations = self.env['board.nominee'].search([('name', '=', self.id)])
        board_nominations = []
        if nominations:
            for n in nominations:
                board_nominations.append(n.nomination_id.id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Board Membership Nomination',
            'res_model': 'board.membership.nomination',
            'domain': [('id', '=', board_nominations)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    @api.onchange('mobile')
    def _check_mobile_format(self):
        for record in self:
            if record.mobile and not (len(record.mobile) == 10 and record.mobile.isdigit()):
                raise ValidationError("Mobile number must be exactly 10 digits.")
    

    

    # @api.constrains('identification_number')
    # def _check_id_no_required_if_member(self):
    #     for record in self:
    #         if record.is_member and not record.identification_number:
    #             raise ValidationError(_("ID number is required for members."))

    @api.constrains('mobile','is_member')
    def _check_mobile_required_if_member(self):
         for record in self:
             if record.is_member and not record.mobile:
                 raise ValidationError(_("Mobile number is required for members."))

 
    

    

    @api.constrains('mobile', 'identification_number','email')
    def _check_unique_mobile_id(self):
         for record in self:
             if record.mobile:
                 existing_mobile = self.search([
                     ('mobile', '=', record.mobile),
                     ('id', '!=', record.id)
                 ], limit=1)
                 if existing_mobile:
                     raise ValidationError(_("Mobile number must be unique."))

             if record.identification_number:
                 existing_id = self.search([
                     ('identification_number', '=', record.identification_number),
                     ('id', '!=', record.id)
                 ], limit=1)
                 if existing_id:
                     raise ValidationError(_("ID number must be unique."))

            

   

                 

    @api.onchange('mobile')
    def _check_mobile_format(self):
         print("Test constraint running!")
         for record in self:
             print("Checking mobile format: %s", record.mobile)
             if record.mobile and (len(record.mobile) != 10 or not record.mobile.isdigit()):
                 raise ValidationError(_("Mobile number must be exactly 10 digits."))




            
    
    

    
