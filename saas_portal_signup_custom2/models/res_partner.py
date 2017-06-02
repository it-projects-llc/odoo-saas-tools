# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    business_reg_no = fields.Char('Business Registration No.')
    dnb_number = fields.Char('D&B Number')
    tax_code = fields.Char('Tax code')
