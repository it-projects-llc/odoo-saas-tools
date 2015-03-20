# -*- coding: utf-8 -*-
import werkzeug
from openerp import http
from openerp.http import request
from openerp.addons.auth_oauth.controllers import main as oauth


class SaasClient(http.Controller):

    @http.route('/saas_client/new_database', type='http', auth='none')
    def new_database(self, **post):
        params = werkzeug.url_encode(post)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % params)
