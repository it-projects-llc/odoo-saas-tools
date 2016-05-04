# -*- coding: utf-8 -*-
from openerp import models, fields, api
import requests
import simplejson

import logging
_logger = logging.getLogger(__name__)

try:
    import boto
    from boto.route53.exception import DNSServerError
except:
    _logger.critical('SAAS Route53 Requires the python library Boto which is not \
    found on your installation')



class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    #TODO: create new fields for storing mailgun
    # domain (with default value as self.name),
    # credentials,
    # TX validation records,
    # MX records,
    # CNAME record

    mail_domain = fields.Char('Mail domain', default=lambda self: self.name)

    @api.multi
    def _create_mail_domain_on_mailgun(self):
        '''Creates domain on mailgun and returns smtp credentials'''
        ir_params = self.env['ir.config_parameter']
        api_key = ir_params.get_param('saas_mailgun.saas_mailgun_api_key')
        #TODO:
        # 0) DONE: get api_key from ir.config_parameter
        # 1) generate password
        # 2) take domain name from model record.domain
        # 3) create domain on mailgun using library
        # 4) from return values take TX, MX, CNAME records to be created on DNS server and save them in model
        # 5) from return values take smtp credentials and save them in model


    @api.multi
    def _route53_domain_verification_and_dns(self, domain_info):
        ir_params = self.env['ir.config_parameter']
        aws_access_key_id = ir_params.get_param('saas_route53.saas_route53_aws_accessid')
        aws_secret_access_key = ir_params.get_param('saas_route53.saas_route53_aws_accesskey')

        #TODO:
        # 0) DONE: get access_key_id and secrets_access_key from ir.config_parameter
        # 1) get records to be created from model
        # 2) create the records on Amazon Route53 server



class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def _create_new_database(self, **kw):
        res = super(SaasPortalPlan, self)._create_new_database(**kw)

        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        res = client_obj._create_mail_domain_on_mailgun()
        new_domain_info = simplejson.loads(res)
        client_obj._route53_domain_verification_and_dns(new_domain_info)
        ir_params = self.env['ir.config_parameter']
        api_key = ir_params.get_param('saas_mailgun.saas_mailgun_api_key')
        client_obj.upgrade(payload={'configure_outgoing_mail': smtp_credentials, 'params': [{'key': 'saas_client.mailgun_api_key', 'value': api_key, 'hidden': True}]})
        return res
