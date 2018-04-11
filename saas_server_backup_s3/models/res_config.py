from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'res.config.settings'

    saas_s3_aws_accessid = fields.Char('AWS Access ID')
    saas_s3_aws_accesskey = fields.Char('AWS Secret Key')
    saas_s3_aws_bucket = fields.Char('S3 Bucket')

    @api.multi
    def set_values(self):
        super(SaasPortalConfigWizard, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("saas_s3.saas_s3_aws_accessid", str(int(self.saas_s3_aws_accessid)))
        ICPSudo.set_param("saas_s3.saas_s3_aws_accesskey", self.saas_s3_aws_accesskey)
        ICPSudo.set_param("saas_s3.saas_s3_aws_bucket", self.saas_s3_aws_bucket)

    @api.model
    def get_values(self):
        res = super(SaasPortalConfigWizard, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            saas_s3_aws_accesskey=ICPSudo.get_param('saas_s3.saas_s3_aws_accesskey'),
            saas_s3_aws_bucket=ICPSudo.get_param('saas_s3.saas_s3_aws_bucket'),
            saas_s3_aws_accessid=ICPSudo.get_param('saas_s3.saas_s3_aws_accessid'),
        )
        return res
