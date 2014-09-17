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

import logging
_logger = logging.getLogger(__name__)

class saas_server(http.Controller):
    @http.route(['/saas_server/new_database'], type='http', auth='public')
    @fragment_to_query_string
    def new_database(self, **post):
        _logger.info('new_database post: %s', post)

        state = simplejson.loads(post.get('state'))
        new_db = state.get('d')
        template_db = state.get('db_template')

        demo = False
        action = 'base.open_module_tree' # TODO

        access_token = post['access_token']

        saas_oauth_provider = request.registry['ir.model.data'].xmlid_to_object(request.cr, SUPERUSER_ID, 'saas_server.saas_oauth_provider')

        admin_data = request.registry['res.users']._auth_oauth_rpc(request.cr, SUPERUSER_ID, saas_oauth_provider.validation_endpoint, access_token)

        if admin_data.get("error"):
            raise Exception(admin_data['error'])

        client_id = admin_data.get('client_id')

        openerp.service.db.exp_drop(new_db) # for debug
        #openerp.service.db.exp_create_database(new_db, demo, lang)
        openerp.service.db.exp_duplicate_database(template_db, new_db)

        registry = openerp.modules.registry.RegistryManager.get(new_db)

        with registry.cursor() as cr:
            # update database.uuid
            registry['ir.config_parameter'].set_param(cr, SUPERUSER_ID, 'database.uuid', client_id)

            # save auth data
            oauth_provider_data = {'enabled':True, 'client_id':client_id}
            for attr in ['name','auth_endpoint', 'scope', 'validation_endpoint', 'data_endpoint', 'css_class', 'body']:
                oauth_provider_data[attr] = getattr(saas_oauth_provider, attr)
            oauth_provider_id = registry['auth.oauth.provider'].create(cr, SUPERUSER_ID, oauth_provider_data)
            registry['ir.model.data'].create(cr, SUPERUSER_ID, {
                'name':'saas_oauth_provider',
                'module':'saas_server',
                'noupdate':True,
                'model':'auth.oauth.provider',
                'res_id':oauth_provider_id,
            })

            admin = registry['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID)
            admin.write({'oauth_provider_id':oauth_provider_id,
                         'oauth_uid':admin_data['user_id'],
                         'oauth_access_token':access_token})

            # get action_id
            action_id = registry['ir.model.data'].xmlid_to_res_id(cr, SUPERUSER_ID, action)
        new_db_domain = new_db

        params = {
            'access_token':post['access_token'],
            'state':simplejson.dumps({
                'd':new_db,
                'p':oauth_provider_id,
                'a':action_id
                }),
            'action':action
            }
        scheme = request.httprequest.scheme
        return werkzeug.utils.redirect('{scheme}://{domain}/saas_client/new_database?{params}'.format(scheme=scheme, domain=new_db_domain, params=werkzeug.url_encode(params)))
