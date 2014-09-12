import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.auth_oauth.controllers.main import fragment_to_query_string
import werkzeug
import werkzeug.utils
import datetime
import time
import uuid
from functools import wraps
import simplejson

from openerp.tools.translate import _

class saas_server(http.Controller):
    @http.route(['/saas_server/new_database'], type='http', auth='public')
    @fragment_to_query_string
    def new_database(self, **post):
        # **post:
        # lang
        # module
        # dbname
        # tz
        # client_id
        # access_token


        # TODO install specific modules

        template_db = '8.0-saas-client-template' # TODO
        new_db = post.get('dbname')
        new_db = '8.0-saas-client' # TMP
        openerp.service.db.exp_drop(new_db) # TMP

        dbuser = 'ivann'
        demo = False
        lang = 'ru_RU'
        action = 'base.action_run_ir_action_todo'

        access_token = post['access_token']

        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        admin_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)

        if admin_data.get("error"):
            raise Exception(admin_data['error'])

        #openerp.service.db.exp_create_database(new_db, demo, lang)
        openerp.service.db.exp_duplicate_database(template_db, new_db)

        registry = openerp.modules.registry.RegistryManager.get(new_db)

        with registry.cursor() as cr:
            # create copy of oauth_provider
            oauth_provider_data = {}
            for attr in ['name','auth_endpoint', 'scope', 'validation_endpoint', 'data_endpoint', 'css_class', 'body']:
                oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
            oauth_provider_id = registry['auth.oauth.provider'].create(cr, SUPERUSER_ID, oauth_provider_data)

            admin = registry['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID)
            admin.write({'oauth_provider_id':oauth_provider_id,
                         'oauth_uid':admin_data['user_id'],
                         'oauth_access_token':access_token})

            action_id = registry['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, action)
        new_db_domain = new_db
        new_db_domain = 'localhost:8069' # TMP

        params = {
            'access_token':post['access_token'],
            'state':simplejson.dumps({
                'd':new_db,
                'p':oauth_provider_id,
                'a':action_id
                }),
            'action':action
            }

        return werkzeug.utils.redirect('http://%s/saas_client/new_database?%s' % (new_db_domain, werkzeug.url_encode(params)))
