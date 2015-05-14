# -*- coding: utf-8 -*-
import openerp
from openerp import api, SUPERUSER_ID
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
from openerp.addons.web.controllers.main import db_monodb, login_and_redirect
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
        demo = state.get('demo')
        lang = state.get('lang', 'en_US')
        addons = state.get('addons', [])
        is_template_db = state.get('is_template_db')
        action = 'base.open_module_tree'
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        saas_portal_user = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])
        if is_template_db:
            # TODO: check access right to crete template db
            pass
        client_id = saas_portal_user.get('client_id')
        client_data = {'name':new_db, 'client_id': client_id}
        client = request.env['saas_server.client'].sudo().create(client_data)
        client.create_database(template_db, demo, lang)
        client.install_addons(addons=addons, is_template_db=is_template_db)
        client.update_registry()
        client.prepare_database(
            saas_portal_user = saas_portal_user,
            is_template_db = is_template_db,
            access_token = access_token)

        with client.registry()[0].cursor() as cr:
            client_env = api.Environment(cr, SUPERUSER_ID, request.context)
            oauth_provider_id = client_env.ref('saas_server.saas_oauth_provider').id
            action_id = client_env.ref(action).id

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

    @http.route('/saas_server/edit_database', type='http', auth='public', website=True)
    @fragment_to_query_string
    def edit_database(self, **post):
        _logger.info('edit_database post: %s', post)

        scheme = request.httprequest.scheme
        state = simplejson.loads(post.get('state'))
        domain = state.get('d')

        params = {
            'access_token': post['access_token'],
            'state': simplejson.dumps(state),
        }
        url = '{scheme}://{domain}/saas_client/edit_database?{params}'
        url = url.format(scheme=scheme, domain=domain, params=werkzeug.url_encode(params))
        return werkzeug.utils.redirect(url)

    @http.route('/saas_server/delete_database', type='http', auth='public')
    @fragment_to_query_string
    def delete_database(self, **post):
        _logger.info('delete_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        user_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        # TODO: check access rights

        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])
        if not client:
            raise Exception('Client not found')
        client = client[0]

        openerp.service.db.exp_drop(client.name)
        client.write({'state': 'deleted'})

        # redirect to server
        params = post.copy()
        url = '/web?model={model}&id={id}'.format(model='saas_server.client', id=client.id)
        if not state.get('p'):
            state['p'] = request.env.ref('saas_server.saas_oauth_provider').id
        state['r'] = url
        state['d'] = request.db
        params['state'] = simplejson.dumps(state)
        # FIXME: server doesn't have auth data for admin (server is created manually currently)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(params))


    @http.route(['/saas_server/stats'], type='http', auth='public')
    def stats(self, **post):
        # TODO auth
        request.env['saas_server.client'].update_all()
        res = []
        for client in request.env['saas_server.client'].sudo().search([('state', 'not in', ['draft'])]):
            res.append({
                'name': client.name,
                'state': client.state,
                'client_id': client.client_id,
                'users_len': client.users_len,
                'file_storage': client.file_storage,
                'db_storage': client.db_storage,
            })
        return simplejson.dumps(res)
