# -*- coding: utf-8 -*-
import werkzeug
import openerp
from openerp import http, SUPERUSER_ID
from openerp.http import request
import simplejson
from openerp.addons.auth_oauth.controllers.main import OAuthLogin as Home
from openerp.addons.web.controllers.main import ensure_db


class SaasClient(http.Controller):

    @http.route(['/saas_client/new_database',
                 '/saas_client/edit_database'], type='http', auth='none')
    def new_database(self, **post):
        params = post.copy()
        state = simplejson.loads(post.get('state'))
        if not state.get('p'):
            state['p'] = request.env.ref('saas_server.saas_oauth_provider').id
        params['state'] = simplejson.dumps(state)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(params))


class SaaSClientLogin(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        param_model = request.env['ir.config_parameter']
        suspended = param_model.sudo().get_param('saas_client.suspended', '0')
        page_for_suspended = param_model.sudo().get_param('saas_client.page_for_suspended', '/')
        if suspended == '1':
            return werkzeug.utils.redirect(page_for_suspended, 303)
        return super(SaaSClientLogin, self).web_login(redirect, **kw)
