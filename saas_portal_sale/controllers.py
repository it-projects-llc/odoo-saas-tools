# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import login_redirect


class SaasPortalSale(http.Controller):
    @http.route('/trial', auth='public')
    def index(self, **kw):
        if request.session.uid:
            return request.render('saas_portal_sale.index', {})
        else:
            return login_redirect()
