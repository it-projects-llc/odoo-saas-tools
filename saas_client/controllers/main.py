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

class saas_client(http.Controller):
    @http.route(['/saas_client/new_database'], type='http', auth='none', website=True)
    def new_database(self, **post):
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(post))
