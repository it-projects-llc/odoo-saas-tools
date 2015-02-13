# -*- coding: utf-8 -*-
import werkzeug
from openerp import http


class SaasClient(http.Controller):

    @http.route('/saas_client/new_database', type='http', auth='none')
    def new_database(self, **post):
        params = werkzeug.url_encode(post)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % params)
