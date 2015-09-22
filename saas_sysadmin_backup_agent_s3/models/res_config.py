from openerp import models, fields
from openerp.addons.web.http import request
import urlparse

class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_server.config.settings'

    saas_s3_aws_accessid = fields.Char('AWS Access ID')
    saas_s3_aws_accesskey = fields.Char('AWS Secret Key')
    saas_s3_aws_bucket = fields.Char('S3 Bucket')

    def get_default_saas_s3_aws_accessid(self, cr, uid, ids, context=None):
        saas_s3_aws_accessid = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_s3.saas_s3_aws_accessid", default=None, context=context)
        return {'saas_s3_aws_accessid': saas_s3_aws_accessid  or False}

    def set_saas_s3_aws_accessid (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_s3.saas_s3_aws_accessid", record.saas_s3_aws_accessid  or '', context=context)
            
    def get_default_saas_s3_aws_accesskey(self, cr, uid, ids, context=None):
        saas_s3_aws_accesskey = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_s3.saas_s3_aws_accesskey", default=None, context=context)
        return {'saas_s3_aws_accesskey': saas_s3_aws_accesskey  or False}

    def set_saas_s3_aws_accesskey (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_s3.saas_s3_aws_accesskey", record.saas_s3_aws_accesskey  or '', context=context)
    
    def get_default_saas_s3_aws_bucket(self, cr, uid, ids, context=None):
        saas_s3_aws_bucket = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_s3.saas_s3_aws_bucket", default=None, context=context)
        return {'saas_s3_aws_bucket': saas_s3_aws_bucket  or False}

    def set_saas_s3_aws_bucket (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_s3.saas_s3_aws_bucket", record.saas_s3_aws_bucket  or '', context=context)
