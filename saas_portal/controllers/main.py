import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time
import uuid
from functools import wraps

from openerp.tools.translate import _

import simplejson

class SignupError(Exception):
    pass

class saas_portal(http.Controller):
    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):

        dbname = post['dbname']

        existed = False
        # TODO check is database already taken

        if existed:
            return {"error":{"msg":"database already taken"}}
        else:
            return {"ok":1}


    @http.route(['/saas_portal/book_then_signup'], type='http', auth='public', website=True)
    def book_then_signup(self, **post):
        saas_server = 'http://localhost:8069/' #TODO
        client_id = 'TODO'

        if not saas_server.endswith('/'):
            saas_server = saas_server + '/'
        params = {
            'scope':'userinfo force_login trial skiptheuse',
            'state':simplejson.dumps({
                'd':post.get('dbname'),
                'u':'https://%s.odoo.com' % post.get('dbname'),#FIX odoo.com
            }),
            'redirect_uri':'%ssaas_server/new_database' % saas_server,
            'response_type':'token',
            'client_id':client_id,
        }

        return request.redirect('/oauth2/auth?%s' % werkzeug.url_encode(params))
