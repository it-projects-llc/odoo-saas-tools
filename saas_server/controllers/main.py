# -*- coding: utf-8 -*-
import functools
import datetime
from odoo import api, SUPERUSER_ID
from odoo import http
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string

import werkzeug.utils
import simplejson


import logging
_logger = logging.getLogger(__name__)


def webservice(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception as e:
            _logger.exception(str(e))
            return http.Response(response=str(e), status=500)
    return wrap


class SaasServer(http.Controller):

    @http.route('/saas_server/new_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    @webservice
    def new_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        owner_user = state.get('owner_user')
        new_db = state.get('d')
        host = state.get('h')
        public_url = state.get('public_url')
        trial = state.get('t')
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
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()
        saas_portal_user = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if saas_portal_user.get('user_id') != 1:
            raise Exception('auth error')
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])

        client_data = {
            'name': new_db,
            'client_id': client_id,
            'expiration_datetime': expiration_db,
            'trial': trial,
            'host': host,
        }
        client = request.env['saas_server.client'].sudo().create(client_data)
        res = client.create_database(template_db, demo, lang)
        client.install_addons(addons=addons, is_template_db=is_template_db)
        if disable_mail_server:
            client.disable_mail_servers()
        client.update_registry()
        client.prepare_database(
            tz=tz,
            owner_user=owner_user,
            is_template_db=is_template_db,
            access_token=access_token,
            server_requests_scheme=request.httprequest.scheme,
        )

        if is_template_db:
            res.update({
                'name': client.name,
                'state': client.state,
                'client_id': client.client_id
            })
            return simplejson.dumps(res)

        with client.registry()[0].cursor() as cr:
            client_env = api.Environment(cr, SUPERUSER_ID, request.context)
            oauth_provider_id = client_env.ref('saas_client.saas_oauth_provider').id
            action_id = client_env.ref(action).id

        url = '{public_url}saas_client/new_database'.format(public_url=public_url)
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
    @webservice
    def edit_database(self, **post):
        _logger.info('edit_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        public_url = state.get('public_url')

        params = {
            'access_token': post['access_token'],
            'state': simplejson.dumps(state),
        }
        url = '{public_url}saas_client/edit_database?{params}'
        url = url.format(public_url=public_url, params=werkzeug.url_encode(params))
        return werkzeug.utils.redirect(url)

    @http.route('/saas_server/upgrade_database', type='http', auth='public')
    @fragment_to_query_string
    @webservice
    def upgrade_database(self, **post):
        state = simplejson.loads(post.get('state'))
        data = state.get('data')
        access_token = post['access_token']
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        saas_portal_user = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if saas_portal_user.get('user_id') != 1:
            raise Exception('auth error')
        if saas_portal_user.get("error"):
            raise Exception(saas_portal_user['error'])

        client_id = post.get('client_id')
        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])

        result = client.upgrade_database(data=state.get('data'))
        return simplejson.dumps({client.name: result})

    @http.route('/saas_server/rename_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    @webservice
    def rename_database(self, **post):
        _logger.info('delete_database post: %s', post)
        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        new_dbname = state.get('new_dbname')
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        access_token = post['access_token']
        user_data = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if user_data.get('user_id') != 1:
            raise Exception('auth error')
        if user_data.get("error"):
            raise Exception(user_data['error'])

        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])
        client.rename_database(new_dbname)

    @http.route('/saas_server/delete_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    @webservice
    def delete_database(self, **post):
        _logger.info('delete_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        user_data = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if user_data.get('user_id') != 1:
            raise Exception('auth error')
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
            state['p'] = request.env.ref('saas_server.saas_oauth_provider').sudo().id
        state['r'] = url
        state['d'] = request.db
        params['state'] = simplejson.dumps(state)
        # FIXME: server doesn't have auth data for admin (server is created manually currently)
        # return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(params))
        return werkzeug.utils.redirect('/web')

    @http.route(['/saas_server/ab/css/<dbuuid>.css'], type='http', auth='public')
    def ab_css(self, dbuuid=None):
        content = ''
        message = self._get_message(dbuuid)
        if message:
            content = '''
.odoo .announcement_bar{
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
    background : url(/web/static/src/img/icons/fa-close.png) no-repeat;
    background-size : 15px 15px;
    opacity: 1;
}

.announcement_bar {
    color: # ffffff;
    height: 30px;
    vertical-align: middle !important;
    text-align: center !important;
    width: 100%;

    border: 0 !important;
    margin: 0 !important;
    padding: 8px !important;

    background-color: # 8785C0;
    background-image: -webkit-linear-gradient(135deg, rgba(255, 255, 255, 0.05) 25%, rgba(255, 255, 255, 0) 25%, rgba(255, 255, 255, 0) 50%, rgba(255, 255, 255, 0.05) 50%, rgba(255, 255, 255, 0.05) 75%, rgba(255, 255, 255, 0) 75%, rgba(255, 255, 255, 0) 100% );
    background-size: 40px 40px;
    -webkit-transition: all 350ms ease;
    text-shadow: 0px 0px 2px rgba(0,0,0,0.2);
    box-shadow: 0px 2px 10px rgba(0,0,0,0.38) inset;
    display: none;
}

.announcement_bar a {
    font-weight: bold;
    color: # d3ffb0 !important;
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
    @webservice
    def stats(self, **post):
        _logger.info('sync_server post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        updating_client_ID = state.get('updating_client_ID')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        user_data = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if user_data.get("error"):
            raise Exception(user_data['error'])

        if updating_client_ID:
            request.env['saas_server.client'].sudo().search([('client_id', '=', updating_client_ID)]).update_one()
        else:
            request.env['saas_server.client'].update_all()
        res = []
        for client in request.env['saas_server.client'].sudo().search([('state', 'not in', ['draft'])]):
            res.append({
                'name': client.name,
                'state': client.state,
                'client_id': client.client_id,
                'users_len': client.users_len,
                'max_users': client.max_users,
                'state': client.state,
                'file_storage': client.file_storage,
                'db_storage': client.db_storage,
                'total_storage_limit': client.total_storage_limit,
            })
        return simplejson.dumps(res)

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

    @http.route('/saas_server/backup_database', type='http', website=True, auth='public')
    @fragment_to_query_string
    def backup_database(self, **post):
        _logger.info('backup_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        user_data = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if user_data.get("error"):
            raise Exception(user_data['error'])

        client = request.env['saas_server.client'].sudo().search([('client_id', '=', client_id)])
        if not client:
            raise Exception('Client not found')
        client = client[0]
        result = client.backup_database()
        return simplejson.dumps(result)
