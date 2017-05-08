# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID, exceptions
from openerp.addons.saas_utils import connector, database
from openerp import http
from openerp.tools import config, scan_languages
from openerp.tools.translate import _
from openerp.addons.base.res.res_partner import _tz_get
import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from oauthlib import common as oauthlib_common
import urllib2
import simplejson
import werkzeug
import requests
import random

import logging
_logger = logging.getLogger(__name__)

class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'
    
    @api.one
    def duplicate_database(self, dbname=None, partner_id=None, expiration=None):
        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        server.action_sync_server()

        vals = {'name': dbname,
                'server_id': server.id,
                'plan_id': self.plan_id.id,
                'partner_id': partner_id or self.partner_id.id,
                }
        if expiration:
            now = datetime.now()
            delta = timedelta(hours=expiration)
            vals['expiration_datetime'] = (now + delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id

        scheme = server.request_scheme
        port = server.request_port
        state = {
            'd': client.name,
            'e': client.expiration_datetime,
            'r': '%s://%s:%s/web' % (scheme, port, client.name),
        }
        state.update({'db_template': self.name})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        url = server._request(path='/saas_server/new_database',
                              scheme=scheme,
                              port=port,
                              state=state,
                              client_id=client_id,
                              scope=scope,)[0]
        return url