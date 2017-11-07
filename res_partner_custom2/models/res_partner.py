# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    business_reg_no = fields.Char('Business Registration No.')
    dnb_number = fields.Char('D&B Number')
    tax_code = fields.Char('Tax code')
    establishment_year = fields.Datetime(string='Year of establishment')
    employee_number = fields.Integer(string='Number of employee')
    company_size = fields.Selection(string='Company size', selection='_get_company_sizes', translate=True)
    account_currency_id = fields.Many2one('res.currency', string='Banking account currency')
    previous_year_turnover = fields.Integer(string='Previous year turn-over')
    gender = fields.Selection(string='Gender', selection='_get_genders', translate=True)

    @api.model
    def _get_company_sizes(self):
        company_sizes = [
                ('1-5', _('< 5 employees')),
                ('5-20', _('5 - 20 employees')),
                ('20-50', _('20 - 50 employees')),
                ('50-250', _('20 - 250 employees')),
                ('250-over', _('> 250 employees')),
                ]

        return company_sizes

    def _get_genders(self):
        genders = [
                ('male', _('Male')),
                ('female', _('Female')),
                ]

        return genders
