# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_portal.config.settings'

    saas_mailgun_api_key = fields.Char('Mailgun API Key')

    @api.model
    def get_default_saas_mailgun_api_key(self, fields):
        saas_mailgun_api_key = self.env["ir.config_parameter"].get_param("saas_mailgun.saas_mailgun_api_key", default=None)
        return {'saas_mailgun_api_key': saas_mailgun_api_key or False}

    @api.multi
    def set_saas_mailgun_api_key(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_mailgun.saas_mailgun_api_key", record.saas_mailgun_api_key or '')
