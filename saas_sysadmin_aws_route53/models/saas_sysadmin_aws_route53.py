# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.route53.exception import DNSServerError
except:
    _logger.debug('SAAS Route53 Requires the python library Boto which is not \
    found on your installation')


def _get_route53_conn(env):
    ir_params = env['ir.config_parameter']
    aws_access_key_id = ir_params.get_param('saas_route53.saas_route53_aws_accessid')
    aws_secret_access_key = ir_params.get_param('saas_route53.saas_route53_aws_accesskey')
    if not aws_access_key_id or not aws_secret_access_key:
        raise Warning('Please specify both your AWS Access key and ID')
    return boto.connect_route53(aws_access_key_id, aws_secret_access_key)


class SaasRoute53Zone(models.Model):
    _name = 'saas_sysadmin.route53.zone'

    name = fields.Char('Domain Name', required=True)
    create_zone = fields.Boolean('Create Zone', help="True if you want zone to be created for you. Leave unchecked if zone has already been created manually")
    hosted_zone_ID = fields.Char('Hosted Zone ID', readonly=True)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        zone = super(SaasRoute53Zone, self).create(vals)
        if zone.create_zone:
            conn = _get_route53_conn(self.env)
            # ensure that the period if at the end
            zone_name = vals.get('name')
            res = conn.create_zone(zone_name)
            zone.write({
                       'name': zone_name,
                       'hosted_zone_ID': res.id,  # TODO check if right
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

    aws_hosted_zone_id = fields.Many2one('saas_sysadmin.route53.zone', 'AWS Hosted Zone')

    def _update_zone(self, name=None, value=None, action='add', type='a'):
        '''
        add, update, delete records
        '''
        assert type in ('cname', 'a', 'txt', 'mx')
        if action in ('add', 'write') and value is None:
            raise Warning('This operation requires a supplied value')
        conn = _get_route53_conn(self.env)
        zone = conn.get_zone(self.aws_hosted_zone_id.name)
        method = '%s_%s' % (action, type)
        if action in ('add', 'update'):
            try:
                if type == 'txt' and action == 'add':
                    value = '"' + value + '"'
                    zone.add_record(resource_type=type.upper(), name=name, value=value, ttl=300)
                else:
                    getattr(zone, method)(name, value)
            except DNSServerError as e:
                _logger.critical(e)
                if e.error_code == 'InvalidChangeBatch':
                    method = method.replace('add', 'update')
                    getattr(zone, method)(name, value)
            except Exception as e:
                _logger.exception('Error modifying AWS hosted zone')
        elif action == 'delete':
            try:
                getattr(zone, method)(name)
            except Exception as e:
                _logger.exception('Error modifying AWS hosted zone')
        else:
            raise Warning('Supported zone operation!')

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        server = super(SaasPortalServer, self).create(vals)
        if server.aws_hosted_zone_id:
            server._update_zone(server.name, value=server.ip_address)
        return server

    @api.multi
    def write(self, vals):
        super(SaasPortalServer, self).write(vals)
        for server in self:
            if server.aws_hosted_zone_id:
                if 'ip_address' in vals:
                    self._update_zone(server.name, value=server.ip_address, action='update')
        return True

    @api.multi
    def unlink(self):
        for server in self:
            if server.aws_hosted_zone_id:
                self._update_zone(server.name, action='delete')
        super(SaasPortalServer, self).unlink()
