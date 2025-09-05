# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

from odoo.exceptions import ValidationError


class BoardMembershipNomination(models.Model):
    _name = 'board.membership.nomination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Board Membership Nomination'

    name = fields.Char('Name', required=True)
    start_date = fields.Date('Nomination Start Date')
    end_date = fields.Date('Nomination End Date')
    nominations_committee = fields.Many2many('hr.employee', 'nomination_committee_rel', 'nomination_id', 'employee_id',
                                             string="Nominations Committee")

    board_nominee_ids = fields.One2many('board.nominee', 'nomination_id', string="Candidates")
    notes = fields.Text('Notes')

    state = fields.Selection([
        ('new', 'New'),
        ('nominated', 'Nominated'),
        ('approved', 'Approved'),
        ('voting', 'Voting'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ], default='new', string="Status")


    def action_nominating(self):
        for record in self:
            members = self.env['res.partner'].search([('is_membership_expire', '!=', True)])
            products = self.env['product.product'].search([('nominee', '=', True)])
            record.board_nominee_ids.unlink()
            for member in members:
                for product in products:
                    memberships = self.env['dev.membership'].search([('state', 'in', ['active', 'expire']), ('partner_id', '=', member.id), ('product_id', '=', product.id),('duration', '>=', product.join_period)])
                    if memberships:
                        total_duration = sum(m.duration for m in memberships)

                        self.env['board.nominee'].create({
                            'name': member.id,
                            'mobile': member.mobile,
                            'email': member.email,
                            'membership_type_id': product.id,
                            'membership_level_id': memberships[0].membrship_level.id,
                            'join_date': member.join_date,
                            'subscription_years': total_duration,
                            'status': 'nominated',
                            'nomination_id': record.id,
                            'membership_number': memberships[0].name,
                        })
                    # for m in memberships:
                    #
                    #     b_nominee = self.env['board.nominee'].create([
                    #         {
                    #             'name': member.id,
                    #             'mobile': member.mobile,
                    #             'email': member.email,
                    #             'membership_type_id': product.id,
                    #             'membership_level_id': m.membrship_level.id,
                    #             'join_date': member.join_date,
                    #             'subscription_years': m.duration,
                    #             'status': 'nominated',
                    #             'nomination_id': record.id,
                    #         }
                    #     ])

            record.state = 'nominated'

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_reject(self):
        for record in self:
            record.state = 'rejected'

    def action_back_to_initial(self):
        for record in self:
            for line in record.board_nominee_ids:
                line.unlink()
            record.state = 'new'


    def action_send_invitation_email(self):
        pass

    def action_send_message(self):
        pass


    def unlink(self):
        for record in self:
            if record.state != 'new':
                raise ValidationError(_("You can only delete records in the 'New' state."))
        return super(BoardMembershipNomination, self).unlink()


class BoardNominee(models.Model):
    _name = 'board.nominee'
    _description = 'Board Nominee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.partner', string='Member', required=True)
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    membership_type_id = fields.Many2one('product.product', 'Membership Type')
    membership_level_id = fields.Many2one('membership.level' ,'Membership Level')
    join_date = fields.Date('Join Date')
    subscription_years = fields.Integer('Subscription Years')
    status = fields.Selection([
        ('nominated', 'Nominated'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('board_member', 'Board Member'),
    ], default='nominated', string="Status")
    vote_count = fields.Integer('Votes')
    notes = fields.Text('Notes')
    nomination_id = fields.Many2one('board.membership.nomination', string="Nomination")
    membership_number = fields.Char('Membership Number', readonly=True)

    def action_accept(self):
        for line in self:
            line.status = 'accepted'

    def action_reject(self):
        for line in self:
            line.status = 'rejected'

    def action_board_member(self):
        for line in self:
            line.status = 'board_member'

    def action_back_to_nominated(self):
        for line in self:
            line.status = 'nominated'