from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    saas_route53_aws_accessid = fields.Char('AWS Access ID')
    saas_route53_aws_accesskey = fields.Char('AWS Secret Key')

    @api.multi
    def set_values(self):
        super(SaasPortalConfigWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_route53.saas_route53_aws_accessid", self.saas_route53_aws_accessid)
        ICPSudo.set_param("saas_route53.saas_route53_aws_accesskey", self.saas_route53_aws_accesskey)

    @api.model
    def get_values(self):
        res = super(SaasPortalConfigWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            saas_route53_aws_accessid=ICPSudo.get_param('saas_route53.saas_route53_aws_accessid'),
            saas_route53_aws_accesskey=ICPSudo.get_param('saas_route53.saas_route53_aws_accesskey'),
        )
        return res
