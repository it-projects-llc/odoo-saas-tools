# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.route53.exception import DNSServerError
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

class SaasRoute53Zone(models.Model):
    _name = 'saas_sysdamin.route53.zone'
    
    name = fields.Char('Domain Name', required=True)
    create_zone = fields.Boolean('Create Zone', help="True if you want zone to be created for you. Leave unchecked if zone has already been created manually")
    aws_hosted_zone = fields.Char('AWS Hosted Zone')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):    
        zone = super(SaasRoute53Zone, self).create(vals)    
        if zone.create_zone:
            conn = _get_route53_conn(self.env)
            # ensure that the period if at the end
            
            res = conn.create_zone(zone_name)
            zone.write({
                       'name' : zone_name,
                       'aws_hosted_zone' : res.id,  # TODO check if right
                       })
        return zone
    
    @api.multi
    def unlink(self):
        # let's delete zone if it was created automatically
        for zone in self:
            if zone.create_zone:
                conn = _get_route53_conn(self.env)
                zone = conn.get_zone(zone.name)
                zone.delete()
        return super(SaasRoute53Zone, self).unlink()
                
class SaasPortalServer(models.Model):
    _inherit = 'saas_portal.server'
    
    aws_hosted_zone = fields.Many2one('saas_sysdamin.route53.zone', 'AWS Hosted Zone')
    
    def _update_zone(self, name=None, value=None, action='add', type='a'):
        '''
        add, update, delete records
        '''
        assert type in ('cname', 'a'); 'Only CNAME and A records are supported'
        if action in ('add', 'write') and value == None:
            raise Warning('This operation requires a supplied value')
        conn = _get_route53_conn(self.env)
        zone = conn.get_zone(self.aws_hosted_zone.name)
        method = '%s_%s' % (action, type)
        if action in ('add', 'update'):
            try:
                getattr(zone, method)(name, value)
            except DNSServerError as e:
                if e.error_code == 'InvalidChangeBatch':
                    method = method.replace('add', 'update')
                    getattr(zone, method)(name, value)
        elif action == 'delete':
            getattr(zone, method)(name)
        else:
            raise Warning('Supported zone operation!')
  
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        server = super(SaasPortalServer, self).create(vals)
        if server.aws_hosted_zone:
            server._update_zone(server.name, value=server.ip_address)            
        return server
    
    @api.multi
    def write(self, vals):
        super(SaasPortalServer, self).write(vals)
        for server in self:
            if server.aws_hosted_zone:
                if 'ip_address' in vals:
                    self._update_zone(server.name, value=server.ip_address, action='update')
        return True
    
    @api.multi
    def unlink(self):
        for server in self:
            if server.aws_hosted_zone:
                self._update_zone(server.name, action='delete')
        super(SaasPortalServer, self).unlink()
           
class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'
    
    @api.multi
    def create_template(self):
        assert len(self) == 1, 'This method is applied only for single record'
        plan = self[0]
        plan.server_id._update_zone(plan.template_id.name, value=plan.server_id.name, type='cname') 
        return super(SaasPortalPlan, self).create_template()
    
    @api.multi
    def delete_template(self):
        super(SaasPortalPlan, self).delete_template()
        self[0].template_id.server_id._update_zone(self[0].template_id.name, type='cname', action='delete')
        return True         
    
class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'   
   
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        client = super(SaasPortalClient, self).create(vals)
        if client.server_id.aws_hosted_zone:
            client.server_id._update_zone(client.name, value=client.server_id.name, type='cname')            
        return client
    
    @api.multi
    def write(self, vals):        
        for client in self:
            server = self.env['saas_portal.server'].browse(vals['server_id'])
            if 'server_id' in vals and client.server_id.aws_hosted_zone and server.id != client.server_id.id:
                client.server_id._update_zone(client.name, value=client.server_id.name, type='cname', action='update') 
        super(SaasPortalClient, self).write(vals)    
        return True
    
    @api.multi
    def unlink(self):        
        for client in self:
          if client.server_id.aws_hosted_zone:
            client.server_id._update_zone(client.name, type='cname', action='delete')  
        return super(SaasPortalClient, self).unlink()
