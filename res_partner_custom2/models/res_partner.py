# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    business_reg_no = fields.Char('Business Registration No.')
    dnb_number = fields.Char('D&B Number')
    tax_code = fields.Char('Tax code')
    establishment_year = fields.Datetime()
    employee_number = fields.Integer(string='Number of employee')
    company_size = fields.Selection(string='Company size', selection='_get_company_sizes')
    account_currency_id = fields.Many2one('res.currency', string='Banking account currency')

    @api.model
    def _get_company_sizes(self):
        company_sizes = [
                ('1-5', '< 5 employees'),
                ('5-20', '5 - 20 employees'),
                ('20-50', '20 - 50 employees'),
                ('50-250', '20 - 250 employees'),
                ('250-over', '> 250 employees'),
                ]

        return company_sizes
