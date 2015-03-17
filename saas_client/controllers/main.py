# -*- coding: utf-8 -*-
import werkzeug
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons import web
from openerp.tools import config


class SaasClient(http.Controller):

    @http.route('/saas_client/new_database', type='http', auth='none')
    def new_database(self, **post):
        params = werkzeug.url_encode(post)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % params)


'''
class Session(web.controllers.main.Session):

    @http.route()
    def logout(self, redirect='/web/login'):
        user_model = request.registry.get('res.users')
        user = user_model.browse(request.cr, SUPERUSER_ID, request.uid)
        if user.oauth_provider_id:
            redirect = '%s://%s' % (request.httprequest.scheme,
                                    config.get('db_master'.replace('_', '.')))
        return super(Session, self).logout(redirect)
'''
