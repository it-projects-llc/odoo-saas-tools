# -*- coding: utf-8 -*-
import datetime
import openerp
from openerp import api, SUPERUSER_ID
from openerp import http
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp.addons.web.controllers.main import login_and_redirect
from openerp.addons.saas_utils import connector

import werkzeug.utils
import simplejson


import logging
_logger = logging.getLogger(__name__)

class SaasServer(http.Controller):

    @http.route('/saas_server/backup_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    def backup_database(self, **post):
        _logger.info('backup_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        user_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if user_data.get("error"):
            raise Exception(user_data['error'])

        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])
        if not client:
            raise Exception('Client not found')
        client = client[0]
        result = client.backup_database() 
        return simplejson.dumps(result)
        
