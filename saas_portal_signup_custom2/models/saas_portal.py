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
            'company_name': owner_user.parent_id.name,
            'website': owner_user.parent_id.website,
            'phone': owner_user.parent_id.phone,
            'fax': owner_user.parent_id.fax,
            'city': owner_user.parent_id.city,
            'street': owner_user.parent_id.street,
            'vat': owner_user.parent_id.vat,
            'zip': owner_user.parent_id.zip,
            'country_id': owner_user.parent_id.country_id.id,
            'state_id': owner_user.parent_id.state_id.id,
            'business_reg_no': owner_user.parent_id.business_reg_no,
            'dnb_number': owner_user.parent_id.dnb_number,
            'tax_code': owner_user.parent_id.tax_code,
            'account_currency_id': owner_user.parent_id.account_currency_id.id,
            'is_company': owner_user.is_company,
            'establishment_year': owner_user.parent_id.establishment_year,
            'previous_year_turnover': owner_user.parent_id.previous_year_turnover,
            'company_size': owner_user.parent_id.company_size,
            'sector_data': [(0, 0, {'name': owner_user.parent_id.sector_id.name})],
            'sector_id': owner_user.sector_id.id,
            'child_ids': [(5, 0, 0)] + [(0, 0, {'name': child.name,
                'gender': child.gender,
                'birthdate_date': child.birthdate_date,
                'function': child.function}) for child in owner_user.child_ids],
            'lang': owner_user.lang,
        })
        return owner_user_data


    @api.multi
    def create_new_database(self, **kwargs):
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)
        client_obj = self.env['saas_portal.client'].browse(res.get('id'))

        payload = {
                'access_owner_add': ['base.group_system'],
                # 'access_owner_add': ['base.group_erp_manager'],
                # 'install_addons': ['access_restricted'],
                }
        client_obj.upgrade(payload=payload)
        payload = {
                'install_addons': ['access_restricted', 'access_apps'],
                }
        client_obj.upgrade(payload=payload)
        return res

    @api.multi
    def create_template(self, **kwargs):
        res = super(SaasPortalPlan, self).create_template(**kwargs)
        if self.template_id:
            self.template_id.upgrade(payload={'install_addons': ['res_partner_custom2']})
