# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_server.config.settings'

    saas_s3_aws_accessid = fields.Char('AWS Access ID')
    saas_s3_aws_accesskey = fields.Char('AWS Secret Key')
    saas_s3_aws_bucket = fields.Char('S3 Bucket')

    @api.model
    def get_default_saas_s3_aws_accessid(self, fields):
        saas_s3_aws_accessid = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_accessid", default=None)
        return {'saas_s3_aws_accessid': saas_s3_aws_accessid or False}

    @api.multi
    def set_saas_s3_aws_accessid(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_accessid", record.saas_s3_aws_accessid or '')

    @api.model
    def get_default_saas_s3_aws_accesskey(self, fields):
        saas_s3_aws_accesskey = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_accesskey", default=None)
        return {'saas_s3_aws_accesskey': saas_s3_aws_accesskey or False}

    @api.multi
    def set_saas_s3_aws_accesskey(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_accesskey", record.saas_s3_aws_accesskey or '')

    @api.model
    def get_default_saas_s3_aws_bucket(self, fields):
        saas_s3_aws_bucket = self.env["ir.config_parameter"].get_param("saas_s3.saas_s3_aws_bucket", default=None)
        return {'saas_s3_aws_bucket': saas_s3_aws_bucket or False}

    @api.multi
    def set_saas_s3_aws_bucket(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("saas_s3.saas_s3_aws_bucket", record.saas_s3_aws_bucket or '')
