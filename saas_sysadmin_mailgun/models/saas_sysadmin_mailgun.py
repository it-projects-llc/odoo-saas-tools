# -*- coding: utf-8 -*-
from openerp import models, fields, api
import requests

import logging
_logger = logging.getLogger(__name__)


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    #TODO: create new fields for storing mailgun
    # domain (with default value as self.name),
    # credentials,
    # TX validation records,
    # MX records,
    # CNAME record

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
    def _validate_mail_domain_using_route53(self):
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


        #PROBLEM:
        # How to send mail credentials to the server and then save them in client database?
        # state = {
        #     'd': client.name,
        #     'e': trial and trial_expiration_datetime or client.create_date,
        #     'r': '%s://%s:%s/web' % (scheme, client.name, port),
        #     'owner_user': owner_user_data,
        #     't': client.trial,
        # }
        # if self.template_id:
        #     state.update({'db_template': self.template_id.name})
        # scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']

        # url = server._request_server(path='/saas_server/new_database',
        #                       scheme=scheme,
        #                       port=port,
        #                       state=state,
        #                       client_id=client_id,
        #                       scope=scope,)[0]
        # res = requests.get(url, verify=(self.server_id.request_scheme == 'https' and self.server_id.verify_ssl))
        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        smtp_credentials = client_obj._create_mail_domain_on_mailgun()
        client_obj._validate_mail_domain_using_route53()
        ir_params = self.env['ir.config_parameter']
        api_key = ir_params.get_param('saas_mailgun.saas_mailgun_api_key')
        client_obj.upgrade(payload={'configure_outgoing_mail': smtp_credentials, 'params': [{'key': 'saas_client.mailgun_api_key', 'value': api_key, 'hidden': True}]})
        return res
