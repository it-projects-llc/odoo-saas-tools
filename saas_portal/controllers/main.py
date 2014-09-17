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
import uuid
import random

class SignupError(Exception):
    pass

class saas_portal(http.Controller):
    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):

        dbname = post['dbname']
        full_dbname = self.get_full_dbname(dbname)

        existed = openerp.service.db.exp_db_exist(full_dbname)

        if existed:
            return {"error":{"msg":"database already taken"}}
        else:
            return {"ok":1}


    @http.route(['/saas_portal/book_then_signup'], type='http', auth='public', website=True)
    def book_then_signup(self, **post):
        saas_server_list = request.registry['ir.config_parameter'].get_param(request.cr, SUPERUSER_ID, 'saas_portal.saas_server_list')
        saas_server_list = saas_server_list.split(',')
        saas_server = saas_server_list[random.randint(0, len(saas_server_list)-1)]
        client_id = str(uuid.uuid1())
        scheme = request.httprequest.scheme
        full_dbname = self.get_full_dbname(post.get('dbname'))
        dbtemplate = request.registry['ir.config_parameter'].get_param(request.cr, SUPERUSER_ID, 'saas_portal.dbtemplate')

        request.registry['oauth.application'].create(request.cr, SUPERUSER_ID, {'client_id': client_id, 'name':full_dbname})

        params = {
            'scope':'userinfo force_login trial skiptheuse',
            'state':simplejson.dumps({
                'd':full_dbname,
                'u':'%s://%s' % (scheme, full_dbname),
                'db_template': dbtemplate,
            }),
            'redirect_uri':'{scheme}://{saas_server}/saas_server/new_database'.format(scheme=scheme, saas_server=saas_server),
            'response_type':'token',
            'client_id':client_id,
        }

        return request.redirect('/oauth2/auth?%s' % werkzeug.url_encode(params))

    def get_full_dbname(self, dbname):
        return '%s.%s' % (dbname, self.get_base_saas_domain())

    def get_base_saas_domain(self):
        return request.registry['ir.config_parameter'].get_param(request.cr, SUPERUSER_ID, "saas_portal.base_saas_domain")

    @http.route(['/page/website.start', '/page/start'], type='http', auth="public", website=True)
    def start(self, **post):

        base_saas_domain = self.get_base_saas_domain()

        values = {
            'base_saas_domain': base_saas_domain,
        }
        return request.website.render("website.start", values)
