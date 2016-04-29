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
    def _create_mail_domain(self):
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
    def _validate_mail_domain(self):
        ir_params = env['ir.config_parameter']
        aws_access_key_id = ir_params.get_param('saas_route53.saas_route53_aws_accessid')
        aws_secret_access_key = ir_params.get_param('saas_route53.saas_route53_aws_accesskey')
        #TODO:
        # 0) DONE: get access_key_id and secrets_access_key from ir.config_parameter
        # 1) get records to be created from model
        # 2) create the records on Amazon Route53 server


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    free_subdomains = fields.Boolean(help='allow to choose subdomains for trials otherwise allow only after payment', default=True)
    non_trial_instances = fields.Selection([('from_trial', 'From trial'), ('create_new', 'Create new')], string='Non-trial instances',
                                           help='Whether to use trial database or create new one when user make payment', required=True, default='create_new')

    @api.multi
    def _create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=False, trial=False, support_team_id=None, async=None):
        res = super(SaasPortalPlan, self)._create_new_database(dbname=dbname,
                                                              client_id=client_id,
                                                              partner_id=partner_id,
                                                              user_id=user_id,
                                                              notify_user=notify_user,
                                                              trial=trial,
                                                              support_team_id=support_team_id,
                                                              async=async)
        #PROBLEM:
        # How to send mail credentials to the server and then save them in client database?
        return res
