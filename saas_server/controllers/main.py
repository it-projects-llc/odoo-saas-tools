# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp.addons.web.controllers.main import db_monodb
from openerp.addons.saas_utils import connector

import werkzeug.utils
import simplejson


import logging
_logger = logging.getLogger(__name__)

class SaasServer(http.Controller):

    @http.route('/saas_server/new_database', type='http', auth='public')
    @fragment_to_query_string
    def new_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        new_db = state.get('d')
        template_db = state.get('db_template')
        action = 'base.open_module_tree'
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        saas_portal_user = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])
        client_id = saas_portal_user.get('client_id')

        context = state.copy()
        context['saas_portal_user'] = saas_portal_user
        context['access_token'] = access_token
        client_data = {'name':new_db, 'client_id': client_id}
        client = request.env['saas_server.client'].with_context(**context).create(client_data)
        params = {
            'access_token': post['access_token'],
            'state': simplejson.dumps({
                'd': new_db,
                'p': oauth_provider_id,
                'a': action_id
                }),
            'action': action
            }
        scheme = request.httprequest.scheme
        return werkzeug.utils.redirect('{scheme}://{domain}/saas_client/new_database?{params}'.format(scheme=scheme, domain=new_db.replace('_', '.'), params=werkzeug.url_encode(params)))

    @http.route('/saas_server/delete_database', type='http', auth='public')
    @fragment_to_query_string
    def delete_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = 'TODO'
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        admin_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        # TODO: check access rights

        client = request.registry['saas_server.client'].search(request.cr, SUPERUSER_ID, [('client_id', '=', client_id)])
        if not client:
            raise Exception('Client not found')
        client = client[0]

        openerp.service.db.exp_drop(client.name)
        client.write({'state': 'deleted'})

        return werkzeug.utils.redirect('/web?model={model}&id={id}'.format(model='saas_server.client', id=client.id))


    @http.route(['/saas_server/stats'], type='http', auth='public')
    def stats(self, **post):
        # TODO auth
        server_db = db_monodb()
        res = request.registry['saas_server.client'].update_all(request.cr, SUPERUSER_ID, server_db)
        return simplejson.dumps(res)
