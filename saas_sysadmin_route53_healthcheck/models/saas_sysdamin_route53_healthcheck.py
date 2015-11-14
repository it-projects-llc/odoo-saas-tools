# -*- coding: utf-8 -*-
import logging
from boto.route53.zone import Zone
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.route53.healthcheck import HealthCheck
except:
    _logger.critical('SAAS Route53 Requires the python library Boto which is not \
    found on your installation')
    
from openerp import models, fields, api
from openerp.exceptions import Warning


def _get_route53_conn(env):
    ir_params = env['ir.config_parameter']
    aws_access_key_id = ir_params.get_param('saas_route53.saas_route53_aws_accessid')
    aws_secret_access_key = ir_params.get_param('saas_route53.saas_route53_aws_accesskey')
    if not aws_access_key_id or not aws_secret_access_key:
        raise Warning('Please specify both your AWS Access key and ID')
    return boto.connect_route53(aws_access_key_id, aws_secret_access_key)

class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'
    
    health_check = fields.Boolean(
        default=False,
        help='Enable health check for clients on this server'
    )

class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'   
   
    health_check_ref = fields.Char(readonly=True)
   
    @api.one
    def _delete_health_check(self):
        conn = _get_route53_conn(self.env)
        res = conn.delete_health_check(self.health_check_ref)

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        client = super(SaasPortalClient, self).create(vals)
        if client.server_id.health_check:
            check = HealthCheck(client.server_id.ip_address, 443, 'HTTPS',
                                '/', fqdn=client.name)
            conn = _get_route53_conn(self.env)
            result = conn.create_health_check(check)
            if result:
                client.health_check_ref = (
                    result['CreateHealthCheckResponse']['HealthCheck']['Id']
                )
            else:
                _logger.error(
                    'Could not create health check for %s'% (client.name))
        return client
    

    @api.multi
    def unlink(self):   
        self.filtered('health_check_ref')._delete_health_check() 
        return super(SaasPortalClient, self).unlink()

    @api.multi
    def delete_database(self):
        res = super(SaasPortalClient, self).delete_database()
        self.filtered('health_check_ref')._delete_health_check()
        self.write({'health_check_ref' : False})
        return res
