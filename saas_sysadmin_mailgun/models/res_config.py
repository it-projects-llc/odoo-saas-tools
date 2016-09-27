# -*- coding: utf-8 -*-
from openerp import models, fields


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_portal.config.settings'

    saas_mailgun_api_key = fields.Char('Mailgun API Key')

    def get_default_saas_mailgun_api_key(self, cr, uid, ids, context=None):
        saas_mailgun_api_key = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_mailgun.saas_mailgun_api_key", default=None, context=context)
        return {'saas_mailgun_api_key': saas_mailgun_api_key or False}

    def set_saas_mailgun_api_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_mailgun.saas_mailgun_api_key", record.saas_mailgun_api_key or '', context=context)
