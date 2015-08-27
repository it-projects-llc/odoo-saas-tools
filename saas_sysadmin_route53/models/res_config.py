from openerp import models, fields
from openerp.addons.web.http import request
import urlparse

class SaasPortalConfigWizard(models.TransientModel):
    _inherit = 'saas_portal.config.settings'

    saas_route53_aws_accessid = fields.Char('AWS Access ID')
    saas_route53_aws_accesskey = fields.Char('AWS Access Key')

    def get_default_saas_route53_aws_accessid(self, cr, uid, ids, context=None):
        saas_route53_aws_accessid = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_route53.saas_route53_aws_accessid", default=None, context=context)
        return {'saas_route53_aws_accessid': saas_route53_aws_accessid  or False}

    def set_saas_route53_aws_accessid (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_route53.saas_route53_aws_accessid", record.saas_route53_aws_accessid  or '', context=context)
            
    def get_default_saas_route53_aws_accesskey(self, cr, uid, ids, context=None):
        saas_route53_aws_accesskey = self.pool.get("ir.config_parameter").get_param(cr, uid, "saas_route53.saas_route53_aws_accesskey", default=None, context=context)
        return {'saas_route53_aws_accesskey': saas_route53_aws_accesskey  or False}

    def set_saas_route53_aws_accesskey (self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "saas_route53.saas_route53_aws_accesskey", record.saas_route53_aws_accesskey  or '', context=context)
