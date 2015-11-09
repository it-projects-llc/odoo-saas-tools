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

    @http.route('/saas_server/new_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    def new_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        owner_user = state.get('owner_user')
        new_db = state.get('d')
        expiration_db = state.get('e')
        template_db = state.get('db_template')
        disable_mail_server = state.get('disable_mail_server', False)
        demo = state.get('demo')
        lang = state.get('lang', 'en_US')
        tz = state.get('tz')
        addons = state.get('addons', [])
        is_template_db = state.get('is_template_db')
        action = 'base.open_module_tree'
        access_token = post['access_token']

        client_id = post['client_id']
        if is_template_db:
            # TODO: check access right to create template db
            saas_portal_user = None
        else:
            saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')
            saas_portal_user = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
            if saas_portal_user.get("error"):
                raise Exception(saas_portal_user['error'])

        client_data = {'name':new_db, 'client_id': client_id, 'expiration_datetime': expiration_db}
        client = request.env['saas_server.client'].sudo().create(client_data)
        client.create_database(template_db, demo, lang)
        client.install_addons(addons=addons, is_template_db=is_template_db)
        if disable_mail_server:
            client.disable_mail_servers()
        client.update_registry()
        client.prepare_database(
            tz=tz,
            owner_user = owner_user,
            is_template_db = is_template_db,
            access_token = access_token)

        if is_template_db:
            res = [{
                'name': client.name,
                'state': client.state,
                'client_id': client.client_id
            }]
            return simplejson.dumps(res)

        with client.registry()[0].cursor() as cr:
            client_env = api.Environment(cr, SUPERUSER_ID, request.context)
            oauth_provider_id = client_env.ref('saas_server.saas_oauth_provider').id
            action_id = client_env.ref(action).id

        port = self._get_port()
        scheme = request.httprequest.scheme
        url = '{scheme}://{domain}:{port}/saas_client/new_database'.format(scheme=scheme, domain=new_db, port=port)
        return simplejson.dumps({
            'url': url,
            'state': simplejson.dumps({
                'd': new_db,
                'p': oauth_provider_id,
                'a': action_id
                }),
        })

    @http.route('/saas_server/edit_database', type='http', auth='public', website=True)
    @fragment_to_query_string
    def edit_database(self, **post):
        _logger.info('edit_database post: %s', post)

        scheme = request.httprequest.scheme
        port = self._get_port()
        state = simplejson.loads(post.get('state'))
        domain = state.get('d')

        params = {
            'access_token': post['access_token'],
            'state': simplejson.dumps(state),
        }
        url = '{scheme}://{domain}:{port}/saas_client/edit_database?{params}'
        url = url.format(scheme=scheme, domain=domain, port=port, params=werkzeug.url_encode(params))
        return werkzeug.utils.redirect(url)

    @http.route('/saas_server/upgrade_database', type='http', auth='public')
    @fragment_to_query_string
    def upgrade_database(self, **post):
        state = simplejson.loads(post.get('state'))
        data = state.get('data')
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        saas_portal_user = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])

        client_id = post.get('client_id')
        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])
        result = client.upgrade_database(data=state.get('data'))[0]
        return simplejson.dumps({client.name: result})

    @http.route('/saas_server/delete_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    def delete_database(self, **post):
        _logger.info('delete_database post: %s', post)

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
            if not state.get('force_delete'):
                raise Exception('Client not found')
            client = request.env['saas_server.client'].sudo().create({'name': db, 'client_id': client_id})
        client = client[0]
        client.delete_database()

        # redirect to server
        params = post.copy()
        url = '/web?model={model}&id={id}'.format(model='saas_server.client', id=client.id)
        if not state.get('p'):
            state['p'] = request.env.ref('saas_server.saas_oauth_provider').id
        state['r'] = url
        state['d'] = request.db
        params['state'] = simplejson.dumps(state)
        # FIXME: server doesn't have auth data for admin (server is created manually currently)
        #return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(params))
        return werkzeug.utils.redirect('/web')

    @http.route(['/saas_server/ab/css/<dbuuid>.css'], type='http', auth='public')
    def ab_css(self, dbuuid=None):
        content = ''
        message = self._get_message(dbuuid)
        if message:
            content = '''
.openerp .announcement_bar{
        display:block;
}

.announcement_bar>span.message:before{
    content: %s
}

.announcement_bar>.url>a:before{
    content: 'Contact Us'
}

.announcement_bar .close {
    height: 15px;
    width: 15px;
    background : url(/web/static/src/img/icons/gtk-close.png) no-repeat;
    background-size : 15px 15px;
    opacity: 1;
}

.announcement_bar {
    color: #ffffff;
    height: 30px;
    vertical-align: middle !important;
    text-align: center !important;
    width: 100%;

    border: 0 !important;
    margin: 0 !important;
    padding: 8px !important;

    background-color: #8785C0;
    background-image: -webkit-linear-gradient(135deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0) 25%, rgba(255, 255, 255, 0) 50%, rgba(255, 255, 255, 0.05) 50%, rgba(255, 255, 255, 0.05) 75%, rgba(255, 255, 255, 0) 75%, rgba(255, 255, 255, 0) 100% );
    background-size: 40px 40px;
    -webkit-transition: all 350ms ease;
    text-shadow: 0px 0px 2px rgba(0,0,0,0.2);
    box-shadow: 0px 2px 10px rgba(0,0,0,0.38) inset;
    display: none;
}

.announcement_bar a {
    font-weight: bold;
    color: #d3ffb0 !important;
    text-decoration: none !important;
    border-radius: 3px;
    padding: 5px 8px;
    cursor: pointer;
    -webkit-transition: all 350ms ease;
}
        '''
            content = content.replace('%s', message)
        return http.Response(content, mimetype='text/css')


    @http.route(['/saas_server/sync_server'], type='http', auth='public')
    def stats(self, **post):
        _logger.info('sync_server post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        user_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)
        if user_data.get("error"):
            raise Exception(user_data['error'])

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
    
    def _get_port(self):
        host_parts = request.httprequest.host.split(':')
        return len(host_parts) > 1 and host_parts[1] or 80
    
    def _get_message(self, dbuuid):
        message = False
        domain = [('client_id', '=', dbuuid)]
        client = request.env['saas_server.client'].sudo().search(domain)
        if client:
            diff = datetime.datetime.strptime(client.expiration_datetime, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.datetime.now()
            hours_remaining = diff.seconds / 3600 + 1
            plural = hours_remaining > 1 and 's' or ''
            message = _("'You use a live preview. The database will be destroyed after %s hour%s.'") % (str(hours_remaining), plural)
        return message
