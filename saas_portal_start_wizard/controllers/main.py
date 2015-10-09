# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID, exceptions
from openerp.addons.saas_portal_start.controllers.main import SaasPortalStart



import werkzeug
import logging
import simplejson

_logger = logging.getLogger(__name__)


class SaasPortalStartWizard(SaasPortalStart):

    @http.route(['/page/website.start', '/page/start'], type='http',
                auth="user", website=True)
    def start(self, **post):
        return super(SaasPortalStartWizard, self).start(**post)

    @http.route(['/page/start/wizard'], type='http', auth="user", website=True)
    def start_wizard(self, **post):
        state = dict(post)

        # Get available plans
        plan_model = request.registry['saas_portal.plan']
        domain = [('state', '=', 'confirmed')]
        ids = plan_model.search(request.cr, SUPERUSER_ID, domain)
        plans = plan_model.browse(request.cr, SUPERUSER_ID, ids)

        plan_data = []
        for plan in plans:
            data = {
                "id": plan.id,
                "name": plan.name,
                "logo": "",
                "desc": plan.summary or ""
            }
            if plan.logo:
                data.update({
                    "logo": "{hook}?model={model}&id={id_}&field={field}".format(
                        hook="/web/binary/image",
                        model="saas_portal.plan",
                        id_=plan.id, field="logo"
                    )
                })
            plan_data.append(data)
        state.update({"plans": plan_data})

        company = request.registry['ir.model.data'].xmlid_to_object(
            request.cr,
            SUPERUSER_ID,
            "base.main_company")
        state.update({"terms": company.terms_n_conds or False})

        addon_model = request.registry['ir.module.module']
        domain = [('application', '=', True)]
        ids = addon_model.search(request.cr, SUPERUSER_ID, domain)
        addons = addon_model.browse(request.cr, SUPERUSER_ID, ids)

        addon_data = []
        for addon in addons:
            data = {
                "name": addon.shortdesc,
                "summ": addon.summary,
                "id": addon.name,
                "logo": addon.icon,
            }
            addon_data.append(data)
        state.update({"addons": addon_data})

        return request.website.render("saas_portal_start_wizard.wizard_tpl", state)

    @http.route(['/saas_portal/add_new_client'], type='http', auth='user',
                website=True)
    def add_new_client(self, **post):
        if not post.get("plan_id", False):
            return werkzeug.utils.redirect(
                '/page/start/wizard?{}'.format(werkzeug.url_encode(post)))

        post.update({"plan_id": int(post["plan_id"])})

        dbname = self.get_full_dbname(post.get('dbname'))
        plan = self.get_plan(post.get('plan_id'))
        url = plan.create_new_database(dbname)[0]

        base, params = url.split("?")
        params = werkzeug.url_decode(params)
        state = simplejson.loads(params['state'])

        addons = []
        if post.get('addons', False):
            addons = post['addons'].split(",")
        state.update({'addons': addons})

        company_data = {
            "name": post.get("company"),
            "vat": post.get("vat"),
            "phone": post.get("phone"),
            "city": post.get("city"),
            "state": post.get("state"),
            "country": post.get("country"),
            "zip": post.get("zip"),
        }

        state.update({"company_data": company_data})
        params['state'] = simplejson.dumps(state)

        url = "{base}?{params}".format(base=base, params=werkzeug.url_encode(params))
        _logger.info("\n\nFinal URL: %s\n", url)

        return werkzeug.utils.redirect(url)

