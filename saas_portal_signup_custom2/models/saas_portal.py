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
            'is_company': owner_user.is_company,
            'establishment_year': owner_user.establishment_year,
            'previous_year_turnover': owner_user.previous_year_turnover,
            'company_size': owner_user.company_size,
            'sector_data': [(0, 0, {'name': owner_user.sector_id.name})],
            'sector_id': owner_user.sector_id.id,
            'child_ids': [(5, 0, 0)] + [(0, 0, {'name': child.name,
                'gender': child.gender,
                'birthdate_date': child.birthdate_date,
                'function': child.function}) for child in owner_user.child_ids],
        })
        return owner_user_data


    @api.multi
    def create_new_database(self, **kwargs):
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)
        client_obj = self.env['saas_portal.client'].browse(res.get('id'))

        payload = {
                'access_owner_add': ['base.group_erp_manager'],
                # 'install_addons': ['access_restricted'],
                }
        client_obj.upgrade(payload=payload)
        payload = {
                'install_addons': ['access_restricted'],
                }
        client_obj.upgrade(payload=payload)
        return res