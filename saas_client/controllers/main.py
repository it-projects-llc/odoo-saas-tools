# -*- coding: utf-8 -*-
import werkzeug
from openerp import http
from openerp.http import request
from openerp.addons.auth_oauth.controllers import main as oauth
import simplejson

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
