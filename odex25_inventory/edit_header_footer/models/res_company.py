from odoo import models, fields


class ResCompany(models.Model):
    """Inherit Res Company"""
    _inherit = 'res.company'

    header_left = fields.Html(string="Header Left", sanitize=False)
    header_right = fields.Html(string="Header Right", sanitize=False)
    footer_html = fields.Html(string="Footer", sanitize=False)
