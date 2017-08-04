# -*- coding: utf-8 -*-

from odoo import fields
from odoo import models
from odoo import api


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    on_create = fields.Selection(default='home')

    @api.multi
    def _prepare_owner_user_data(self, owner_user, owner_password):
        owner_user_data = super(SaasPortalPlan, self)._prepare_owner_user_data(owner_user, owner_password)
        owner_user_data.update({
            'company_name': owner_user.company_name,
            'website': owner_user.website,
            'phone': owner_user.phone,
            'fax': owner_user.fax,
            'city': owner_user.city,
            'street': owner_user.street,
            'vat': owner_user.vat,
            'zip': owner_user.zip,
            'country_id': owner_user.country_id.id,
            'state_id': owner_user.state_id.id,
            'business_reg_no': owner_user.business_reg_no,
            'dnb_number': owner_user.dnb_number,
            'tax_code': owner_user.tax_code,
            'account_currency_id': owner_user.account_currency_id.id,
        })
        return owner_user_data
