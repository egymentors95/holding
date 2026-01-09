from odoo import models, fields, api, _


class DriverDriver(models.Model):
    _name = 'driver.driver'
    _description = 'Driver'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(default=_('New'), readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('delivered', 'Delivered'),
        ('refused', 'Refused'),
    ],default='draft', tracking=True, string='Status')
    date = fields.Datetime(string='Date')
    driver_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user,)

    stock_id = fields.Many2one(comodel_name='stock.picking')
    sale_id = fields.Many2one(comodel_name='sale.order')
    driver_line_ids = fields.One2many(comodel_name='driver.line', inverse_name='driver_driver_id')
    total_price = fields.Float(compute='_get_total_price', store=True)
    total_quantity = fields.Float(compute='_get_total_quantity', store=True)
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachments', )
    source = fields.Char(string='Source')

    # --------------------
    # Buttons
    # --------------------
    def button_refuse(self):
        for rec in self:
            rec.state = 'refused'
            rec.stock_id.state2 = 'draft'
            rec.stock_id.driver_id = False

    def button_accept(self):
        for rec in self:
            rec.state = 'waiting'
            rec.stock_id.state2 = 'out_for_delivery'
            rec.sale_id.state2 = 'out_for_delivery'

    def button_confirm(self):
        for rec in self:
            rec.state = 'delivered'
            rec.stock_id.state2 = 'delivered'
            rec.sale_id.state2 = 'delivered'


    # --------------------
    # Compute Methods
    # --------------------
    @api.depends('driver_line_ids.total')
    def _get_total_price(self):
        for rec in self:
            rec.total_price = sum(rec.driver_line_ids.mapped('total'))

    @api.depends('driver_line_ids.quantity')
    def _get_total_quantity(self):
        for rec in self:
            rec.total_quantity = sum(rec.driver_line_ids.mapped('quantity'))

    # --------------------
    # Create (Sequence)
    # --------------------
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.driver', ) or _('New')

        return super(DriverDriver, self).create(vals)



class DriverLines(models.Model):
    _name = 'driver.line'
    _description = 'Driver Lines'

    driver_driver_id = fields.Many2one(comodel_name='driver.driver')

    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    location_id = fields.Many2one(comodel_name='stock.location', string='From')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one(comodel_name='uom.uom', string='UOM')
    price = fields.Float(string='Price')
    total = fields.Float(string='Total', compute='_get_total', store=True)
    date_time = fields.Datetime(string='Date', default=fields.Datetime.now)


    @api.depends('price', 'quantity')
    def _get_total(self):
        for rec in self:
            rec.total = rec.price * rec.quantity
