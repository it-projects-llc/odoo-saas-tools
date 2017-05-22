# -*- coding: utf-8 -*-
from odoo import models, api


BASE_SAAS_DOMAIN = 'saas_portal.base_saas_domain'

class IrConfigParameter(models.Model):

    _inherit = 'ir.config_parameter'

    @api.model
    def set_param(self, key, value, groups=()):
        if key == 'web.base.url' and not self.get_param(BASE_SAAS_DOMAIN):
            domain_only = value
            if '/' in domain_only:
                # get rid of "http(s)://" at the beggining and "/" and the end if any
                domain_only = domain_only.split('/')[2]
            self.set_param(BASE_SAAS_DOMAIN, domain_only)
        return super(IrConfigParameter, self).set_param(key, value, groups=groups)
