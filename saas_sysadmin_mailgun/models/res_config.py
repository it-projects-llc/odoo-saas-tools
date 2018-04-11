from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    saas_mailgun_api_key = fields.Char('Mailgun API Key')

    @api.multi
    def set_values(self):
        super(SaasPortalConfigWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_mailgun.saas_mailgun_api_key", self.saas_mailgun_api_key)

    @api.model
    def get_values(self):
        res = super(SaasPortalConfigWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            saas_mailgun_api_key=ICPSudo.get_param('saas_mailgun.saas_mailgun_api_key'),
        )
        return res
