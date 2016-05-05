# -*- coding: utf-8 -*-
from openerp import models, fields, api
import simplejson
import mailgun

import logging
_logger = logging.getLogger(__name__)

try:
    pass
except:
    _logger.critical('SAAS Route53 Requires the python library Boto which is not \
    found on your installation')


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    mail_domain = fields.Char('Mail domain', default=lambda self: self.name.split('.')[0] + '.' + self.server_id.aws_hosted_zone_id.name)

    @api.multi
    def _create_domain_on_mailgun(self):
        self.ensure_one()
        '''Creates domain on mailgun and returns domain and configuration info'''
        ir_params = self.env['ir.config_parameter']
        api_key = ir_params.get_param('saas_mailgun.saas_mailgun_api_key')
        password = 'secretpassword'
        mailgun.add_domain(api_key=api_key, domain_name=self.mail_domain, smtp_password=password)

    @api.multi
    def _domain_verification_and_dns_route53(self, domain_info):
        self.ensure_one()
        receiving_dns_records = domain_info.get('receiving_dns_records')
        name = self.mail_domain
        for r in receiving_dns_records:
            value = r.get('priority') + ' ' + r.get('value') + '\n'
        self.server_id._update_zone(name=name, type='mx', value=value)

        sending_dns_records = domain_info.get('sending_dns_records')
        for r in sending_dns_records:
            self.server_id._update_zone(name=r['name'], type=r['record_type'].lower, value=r['value'])


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def _create_new_database(self, **kw):
        res = super(SaasPortalPlan, self)._create_new_database(**kw)

        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        res = client_obj._create_domain_on_mailgun()
        new_domain_info = simplejson.loads(res)
        client_obj._route53_domain_verification_and_dns(new_domain_info)

        ir_params = self.env['ir.config_parameter']
        api_key = ir_params.get_param('saas_mailgun.saas_mailgun_api_key')
        client_obj.upgrade(payload={'configure_outgoing_mail': new_domain_info['domain'], 'params': [{'key': 'saas_client.mailgun_api_key', 'value': api_key, 'hidden': True}]})
        return res
