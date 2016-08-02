# -*- coding: utf-8 -*-
import werkzeug
import simplejson
import openerp
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.saas_server.controllers.main import SaasServer, webservice
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class SaasServerDemo(SaasServer):

    @http.route('/saas_server/restart', type='http', website=True, auth='public')
    @fragment_to_query_string
    @webservice
    def restart_saas_server(self, **post):
        _logger.info('restart_saas_server post: %s', post)

        access_token = post['access_token']

        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()
        saas_portal_user = request.registry['res.users']._auth_oauth_rpc(request.cr,
                                                                         SUPERUSER_ID,
                                                                         saas_oauth_provider.validation_endpoint,
                                                                         access_token,
                                                                         local_ip=saas_oauth_provider.local_ip,
                                                                         local_port=saas_oauth_provider.local_port)
        if saas_portal_user.get('user_id') != 1:
            raise Exception('auth error')
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])

        openerp.service.server.restart()

