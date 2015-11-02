# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID, exceptions
from openerp.addons.saas_portal_start.controllers.main import SaasPortalStart

import werkzeug
import logging
import simplejson


_logger = logging.getLogger(__name__)

PAGE_PLAN_SELECT = "page_plan_select"
PAGE_PLAN_CONFIRM = "page_plan_confirm"
PAGE_TERMS_CONDS = "page_terms_conds"
PAGE_ADDONS_SELECT = "page_addons_select"
PAGE_SUMMARY = "page_summary"

WIZARD_FLOW = {
    PAGE_PLAN_SELECT: {
        "prev": None,
        "next": PAGE_TERMS_CONDS,
    },
    PAGE_TERMS_CONDS: {
        "prev": PAGE_PLAN_SELECT,
        "next": PAGE_PLAN_CONFIRM,
    },
    PAGE_PLAN_CONFIRM: {
        "prev": PAGE_TERMS_CONDS,
        "next": PAGE_ADDONS_SELECT,
    },
    PAGE_ADDONS_SELECT: {
        "prev": PAGE_PLAN_CONFIRM,
    #     "next": PAGE_SUMMARY,
    # },
    # PAGE_SUMMARY: {
    #     "prev": PAGE_ADDONS_SELECT,
        "next": None,
    },
}

class SaasPortalStartWizard(SaasPortalStart):

    @http.route(['/page/website.start', '/page/start'], type='http',
                auth="user", website=True)
    def start(self, **post):
        return super(SaasPortalStartWizard, self).start(**post)

    def __get_plans(self, upstream={}):
        # Get available plans
        plan_model = request.registry['saas_portal.plan']
        domain = [('state', '=', 'confirmed')]
        ids = plan_model.search(request.cr, SUPERUSER_ID, domain)
        plans = plan_model.browse(request.cr, SUPERUSER_ID, ids)

        return {"plans": plans}

    def __get_legal(self, upstream={}):
        cr, uid = request.cr, request.uid
        context, registry = request.context, request.registry

        orm_user = registry.get('res.users')
        orm_country = registry.get('res.country')
        orm_state = registry.get('res.country.state')
        payment_obj = request.registry.get('payment.acquirer')
        sale_order_obj = request.registry.get('sale.order')

        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        states_ids = orm_state.search(cr, SUPERUSER_ID, [], context=context)
        states = orm_state.browse(cr, SUPERUSER_ID, states_ids, context)
        partner = orm_user.browse(cr, SUPERUSER_ID, uid, context).partner_id

        values = {
            'name': upstream.pop('name', False) or partner.name or '',
            'phone': upstream.pop('phone', False) or partner.phone or getattr(
                partner.parent_id, "phone", ''),
            'company': upstream.pop('company', False) or getattr(
                partner.parent_id, "name", ''),
            'vat': upstream.pop('vat', False) or getattr(partner.parent_id,
                                                         "vat", ''),
            'city': upstream.pop('city', False) or partner.city or getattr(
                partner.parent_id, "city", ''),
            'zip_': upstream.pop('zip_', False) or partner.zip or getattr(
                partner.parent_id, "zip", ''),
            'country_id': upstream.pop('country_id', False) or getattr(
                partner.country_id or getattr(partner.parent_id, "country_id",
                                              False), "id"),
            'state_id': upstream.pop('state_id', False) or getattr(
                partner.state_id or getattr(partner.parent_id, "state_id",
                                            False), "id"),
            'countries': countries,
            'states': states,
        }

        orm_plan = registry.get('saas_portal.plan')

        plan = orm_plan.browse(cr, uid, int(upstream['plan_id']))
        if hasattr(plan, "pricing"):
            order = plan.get_sale_order(partner.id, upstream.get('dbname'),
                                        True, True)[0]
            _logger.info("\n\nObtained order: %s\n", order)
            shipping_partner_id = False
            if order:
                if order.partner_shipping_id.id:
                    shipping_partner_id = order.partner_shipping_id.id
                else:
                    shipping_partner_id = order.partner_invoice_id.id
                values.update({"order": order})
                errors = sale_order_obj._get_errors(cr, uid, order,
                                                    context=context)
                values.update({'errors': errors})
                web_data = sale_order_obj._get_website_data(cr, uid, order,
                                                            context)
                values.update(web_data)

                acquirer_ids = payment_obj.search(cr, SUPERUSER_ID, [
                    ('website_published', '=', True),
                    ('company_id', '=', order.company_id.id)], context=context)
                values['acquirers'] = list(
                    payment_obj.browse(cr, uid, acquirer_ids, context=context))
                render_ctx = dict(context, submit_class='btn btn-primary',
                                  submit_txt="Pay Now")
                for acquirer in values['acquirers']:
                    acquirer.button = payment_obj.render(
                        cr, SUPERUSER_ID, acquirer.id,
                        order.name,
                        order.amount_total,
                        order.pricelist_id.currency_id.id,
                        partner_id=shipping_partner_id,
                        tx_values={
                            'return_url': '/page/start/wizard/submit?{}'.format(
                                werkzeug.url_encode(upstream)),
                        },
                        context=render_ctx)

        return values

    def __get_terms(self, upstream={}):
        company = request.registry['ir.model.data'].xmlid_to_object(
            request.cr,
            SUPERUSER_ID,
            "base.main_company")

        return {"terms": company.terms_n_conds or False}

    def __get_addons(self, upstream={}):
        addon_model = request.registry['ir.module.module']
        domain = [('application', '=', True)]
        ids = addon_model.search(request.cr, SUPERUSER_ID, domain)
        addons = addon_model.browse(request.cr, SUPERUSER_ID, ids)

        upstream.update({"addons": None})

        return {"addons": addons}

    def __get_metadata(self, upstream={}):
        crumbs = [
            (PAGE_PLAN_SELECT, "Plan selection"),
            (PAGE_TERMS_CONDS, "License agreement"),
            (PAGE_PLAN_CONFIRM, "Legal info"),
            (PAGE_ADDONS_SELECT, "Extra addons"),
        ]

        summary = [
            ("General", [
                ("Tenant name", upstream.get("dbname"))
            ])
        ]

        cr, uid = request.cr, SUPERUSER_ID

        plan_id = upstream.get("plan_id", False)
        if plan_id:
            plan_model = request.registry['saas_portal.plan']
            plan = plan_model.browse(cr, uid, int(plan_id))
            summary.append(
                ("Plan", [
                    ("Name", plan.name)
                ])
            )
            if hasattr(plan, "pricing"):
                BILLING = {
                    "pre": "Pre-paid",
                    "post": "Post-paid",
                }
                PRICING_LABEL = {
                    "fixed": "Price",
                    "variable": "Starting at"
                }

                summary[-1][1].extend([
                    ("Billing", BILLING[plan.pricing.billing]),
                    ("Pricing", plan.pricing.pricing.capitalize()),
                    (PRICING_LABEL[plan.pricing.pricing], plan.pricing.price),
                    ("To be paid", plan.pricing.period.capitalize()),
                ])
            else:
                summary[-1][1].append(("Pricing", "Free"))

        name = upstream.get("name", False)
        if name:
            summary.append((
                "Personal Information", [
                    ("Name", upstream.get("name")),
                    ("Phone", upstream.get("phone")),
                ]
            ))
            address = "{}, Zip: {}.".format(upstream.get("city"),
                                            upstream.get("zip_"))
            state_id = upstream.get("state_id")
            if state_id:
                state_model = request.registry['res.country.state']
                state = state_model.browse(cr, uid, int(state_id))
                address = "{} {},".format(address, state.name)

            country_model = request.registry['res.country']
            country_id = upstream.get('country_id')
            country = country_model.browse(cr, uid, int(country_id))
            address = "{} {}.".format(address, country.name)

            summary.append((
                "Legal Information", [
                    ("Company", upstream.get("company")),
                    ("VAT", upstream.get("vat")),
                    ("Address", address),
                ]
            ))

        data = {"crumbs": crumbs, "summary": summary}
        return data

    def __validate_data(self, upstream):
        cr, uid = request.cr, SUPERUSER_ID
        plan_model = request.registry['saas_portal.plan']
        user_model = request.registry['res.users']

        errors = {}
        errors["general"] = []

        plan_id = upstream.get("plan_id", False)
        if plan_id:
            plan = plan_model.browse(cr, uid, int(plan_id))

            if hasattr(plan, 'pricing'):
                partner = user_model.browse(cr, uid, request.uid).partner_id
                if not partner.customer:
                    errors["general"].append(
                        "User must be costumer to purchase this plan.")
                    errors['plan_id'] = 'has-error'

        return errors

    @http.route(['/page/start/wizard'], type='http', auth="user", website=True)
    def start_wizard(self, **post):
        _logger.info("\n\nWIZARD START with :: %s\n", post)

        state = {"upstream": post.items()}
        state["upstream"].append(("plan_id", None))

        state.update(self.__get_plans())
        state.update({"wizard_page": PAGE_PLAN_SELECT})
        state.update({"meta": self.__get_metadata(post)})

        return request.website.render("saas_portal_start_wizard.wizard_tpl",
                                      state)

    @http.route(['/page/start/wizard/submit'], type='http', auth="user",
                website=True)
    def wizard_submit(self, **post):
        _logger.info("\n\nWIZARD SUBMIT with :: %s\n", post)

        current_page = post.get("wizard_page")
        action = "next" if post.get("page_next", False) is not False else "prev"
        # post.pop("page_prev", False)

        upstream = post.copy()
        state = {"upstream": upstream.items()}

        errors = self.__validate_data(upstream)
        if errors and errors.get('general', []):
            _logger.info("\n\nErrors: %s\n", errors)
            state.update({"errors": errors})
            next_page = current_page
        else:
            next_page = WIZARD_FLOW[current_page][action]

        if (not next_page) and (action == "prev"):
            return werkzeug.utils.redirect('/page/start/')

        if (not next_page) and (action == "next"):
            return werkzeug.utils.redirect(
                '/saas_portal/add_new_client?{}'.format(
                    werkzeug.url_encode(post)
                )
            )

        data = {
            PAGE_PLAN_SELECT: self.__get_plans,
            PAGE_TERMS_CONDS: self.__get_terms,
            PAGE_PLAN_CONFIRM: self.__get_legal,
            PAGE_ADDONS_SELECT: self.__get_addons,
        }[next_page](upstream)

        # state = {"upstream": upstream.items()}
        state.update(data)
        state.update({"meta": self.__get_metadata(upstream)})
        state.update({"wizard_page": next_page})

        _logger.info("\n\nSTATE: %s\n", state)

        return request.website.render("saas_portal_start_wizard.wizard_tpl",
                                      state)

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
            "name": post.get("name"),
            "company": post.get("company"),
            "vat": post.get("vat"),
            "phone": post.get("phone"),
            "city": post.get("city"),
            "state_id": post.get("state_id", False),
            "country_id": post.get("country_id"),
            "zip": post.get("zip_"),
        }

        state.update({"company_data": company_data})
        params['state'] = simplejson.dumps(state)

        url = "{base}?{params}".format(base=base,
                                       params=werkzeug.url_encode(params))
        _logger.info("\n\nFinal URL: %s\n", url)

        return werkzeug.utils.redirect(url)

