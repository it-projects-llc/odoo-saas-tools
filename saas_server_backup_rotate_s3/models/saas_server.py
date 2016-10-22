# -*- coding: utf-8 -*-
from odoo import api
from odoo import models
import psycopg2

import logging
_logger = logging.getLogger(__name__)


try:
    import boto
    from boto.s3.key import Key
except:
    _logger.debug('SAAS Sysadmin Bacnkup Agent S3 Requires the python library Boto which is not \
    found on your installation')

try:
    from rotate_backups_s3 import S3RotateBackups
except:
    _logger.debug('SAAS Server Backup Rotate S3 Requires the python library'
                  'rotate-backups-s3; grab it from pypi')


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    @api.multi
    def _rotate_backups(self, rotation_scheme):
        ir_params = self.env['ir.config_parameter']
        aws_access_key_id = ir_params.get_param('saas_s3.saas_s3_aws_accessid')
        aws_secret_access_key = ir_params.get_param('saas_s3.saas_s3_aws_accesskey')
        aws_s3_bucket = ir_params.get_param('saas_s3.saas_s3_aws_bucket')

        for client in self:
            include_list = [client.name + '*']
            S3RotateBackups(
                rotation_scheme=rotation_scheme,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                include_list=include_list,
            ).rotate_backups(aws_s3_bucket)
