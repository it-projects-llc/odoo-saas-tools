# -*- coding: utf-8 -*-
from odoo import models, fields


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_server.config.settings'

    saas_s3_aws_accessid = fields.Char('AWS Access ID')
    saas_s3_aws_accesskey = fields.Char('AWS Secret Key')
    saas_s3_aws_bucket = fields.Char('S3 Bucket')

    def get_default_saas_s3_aws_accessid(self):
        saas_s3_aws_accessid = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_accessid", default=None)
        return {'saas_s3_aws_accessid': saas_s3_aws_accessid or False}

    def set_saas_s3_aws_accessid(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_accessid", record.saas_s3_aws_accessid or '')

    def get_default_saas_s3_aws_accesskey(self):
        saas_s3_aws_accesskey = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_accesskey", default=None)
        return {'saas_s3_aws_accesskey': saas_s3_aws_accesskey or False}

    def set_saas_s3_aws_accesskey(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_accesskey", record.saas_s3_aws_accesskey or '')

    def get_default_saas_s3_aws_bucket(self):
        saas_s3_aws_bucket = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_bucket", default=None)
        return {'saas_s3_aws_bucket': saas_s3_aws_bucket or False}

    def set_saas_s3_aws_bucket(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_bucket", record.saas_s3_aws_bucket or '')
