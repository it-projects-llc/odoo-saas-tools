# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp import SUPERUSER_ID, exceptions
from openerp.addons.saas_portal_start.controllers.main import SaasPortalStart
from openerp.addons.saas_pricing.controllers.main import SaasPricing

import werkzeug
import logging
import simplejson


_logger = logging.getLogger(__name__)

PAGE_PLAN_SELECT = "page_plan_select"
PAGE_PLAN_CONFIRM = "page_plan_confirm"
PAGE_TERMS_CONDS = "page_terms_conds"
PAGE_PAYMENT = "page_payment"
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
        "next": PAGE_PAYMENT,
    },
    PAGE_PAYMENT: {
        "prev": PAGE_PLAN_CONFIRM,
        "next": PAGE_ADDONS_SELECT,
    },
    PAGE_ADDONS_SELECT: {
        "prev": PAGE_PAYMENT,
        "next": None,
    },
}

class SaasPortalStartWizard(SaasPortalStart):

    @http.route(['/page/website.start', '/page/start'], type='http',
                auth="user", website=True)
    def start(self, **post):
        return super(SaasPortalStartWizard, self).start(**post)

    def __get_plans(self, wz=None):
        # Get available plans
        plan_model = request.registry['saas_portal.plan']
        domain = [('state', '=', 'confirmed')]
        ids = plan_model.search(request.cr, SUPERUSER_ID, domain)
        plans = plan_model.browse(request.cr, SUPERUSER_ID, ids)

        return {"plans": plans}

    def __get_legal(self, wz):
        cr, uid = request.cr, request.uid
        context, registry = request.context, request.registry

        orm_user = registry.get('res.users')
        orm_country = registry.get('res.country')
        orm_state = registry.get('res.country.state')

        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        states_ids = orm_state.search(cr, SUPERUSER_ID, [], context=context)
        states = orm_state.browse(cr, SUPERUSER_ID, states_ids, context)
        partner = orm_user.browse(cr, SUPERUSER_ID, wz.user_id,
                                  context).partner_id

        values = {
            'name': wz.legal_name or '',
            'phone': wz.legal_phone or '',
            'company': wz.legal_company or '',
            'vat': wz.legal_vat or '',
            'city': wz.legal_city or '',
            'zip_': wz.legal_zip or '',
            'country_id': wz.legal_country_id or False,
            'state_id': wz.legal_state_id or False,
            'countries': countries,
            'states': states,
        }

        return values

    def __get_payment_methods(self, wz):
        cr, uid = request.cr, request.uid
        context, registry = request.context, request.registry

        orm_plan = registry.get('saas_portal.plan')
        orm_user = registry.get('res.users')
        payment_obj = request.registry.get('payment.acquirer')
        sale_order_obj = request.registry.get('sale.order')

        _logger.info("\n\nFetching partner for [user: %s]\n", wz.user_id)
        partner = orm_user.browse(cr, SUPERUSER_ID, wz.user_id,
                                  context).partner_id
        _logger.info("\n\nCreating order for [partner: %s]\n", partner)

        plan = orm_plan.browse(cr, SUPERUSER_ID, wz.plan_id)
        values = {}
        if getattr(plan, "pricing", False):
            order = None
            if wz.order_id:
                order_ = sale_order_obj.browse(cr, SUPERUSER_ID, wz.order_id)
                if order_.state != "cancel":
                    order = order_
            if not order:
                order = plan.get_sale_order(partner.id, wz.dbname,
                                            True, True)[0]

            _logger.info("\n\nObtained order: %s with status: %s\n", order, order.state)

            if order and not (order.invoiced or order.state in (
                    "manual", "shipping_except", "invoice_except", "done")):
                message = ""
                if order.state == "sent":
                    message = "A transaction has been registered but it is " \
                              "not confirmed at this moment. Please make " \
                              "sure the transaction has been confirmed and " \
                              "return here."
                values.update({"message": message})

                wz.order_id = order.id
                payload = {
                    "d": wz.dbname,
                }
                if order.partner_shipping_id.id:
                    shipping_partner_id = order.partner_shipping_id.id
                else:
                    shipping_partner_id = order.partner_invoice_id.id
                values.update({"order": order})
                errors = sale_order_obj._get_errors(cr, SUPERUSER_ID, order,
                                                    context=context)
                values.update({'errors': errors})
                web_data = sale_order_obj._get_website_data(cr, SUPERUSER_ID, order,
                                                            context)
                values.update(web_data)

                acquirer_ids = payment_obj.search(cr, SUPERUSER_ID, [
                    ('website_published', '=', True),
                    ('company_id', '=', order.company_id.id)], context=context)
                values['acquirers'] = list(
                    payment_obj.browse(cr, SUPERUSER_ID, acquirer_ids, context=context))
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
                            'return_url': '/page/start/wizard/payment_cb?{}'.format(
                                werkzeug.url_encode(payload)),
                        },
                        context=render_ctx)

        return values

    def __get_terms(self, wz=None):
        company = request.registry['ir.model.data'].xmlid_to_object(
            request.cr,
            SUPERUSER_ID,
            "base.main_company")

        return {"terms": company.terms_n_conds or False}

    def __get_addons(self, wz):
        addon_model = request.registry['ir.module.module']
        domain = [('application', '=', True)]
        ids = addon_model.search(request.cr, SUPERUSER_ID, domain)
        addons = addon_model.browse(request.cr, SUPERUSER_ID, ids)

        # upstream.update({"addons": None})

        return {"addons": addons}

    def __get_metadata(self, wz):
        crumbs = [
            (PAGE_PLAN_SELECT, "Plan selection"),
            (PAGE_TERMS_CONDS, "License agreement"),
            (PAGE_PLAN_CONFIRM, "Billing"),
            # (PAGE_PAYMENT, "Payment methods"),
            (PAGE_ADDONS_SELECT, "Extra addons"),
        ]

        summary = [
            ("General", [
                ("Tenant name", wz.dbname)
            ])
        ]

        cr, uid = request.cr, SUPERUSER_ID

        if wz.plan_id:
            plan_model = request.registry['saas_portal.plan']
            plan = plan_model.browse(cr, uid, wz.plan_id)
            summary.append(
                ("Plan", [
                    ("Name", plan.name)
                ])
            )
            if getattr(plan, "pricing", False):
                crumbs.insert(3, (PAGE_PAYMENT, "Payment methods"))
                WIZARD_FLOW.update({
                })
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

        if wz.legal_name:
            summary.append((
                "Personal Information", [
                    ("Name", wz.legal_name),
                    ("Phone", wz.legal_phone),
                ]
            ))
            address = wz.legal_city or ""
            if wz.legal_zip:
                address += ", Zip: {}.".format(wz.legal_zip)
            if wz.legal_state_id:
                state_model = request.registry['res.country.state']
                state = state_model.browse(cr, uid, wz.legal_state_id)
                address = "{} {},".format(address, state.name)

            country_model = request.registry['res.country']
            country = country_model.browse(cr, uid, wz.legal_country_id)
            if country:
                address += " {}.".format(country.name)

            summary.append((
                "Legal Information", [
                    ("Company", wz.legal_company),
                    ("VAT", wz.legal_vat),
                    ("Address", address),
                ]
            ))

        data = {"crumbs": crumbs, "summary": summary}
        return data

    @http.route(['/page/start/wizard'], type='http', auth="user", website=True)
    def start_wizard(self, **post):
        cr, uid = request.cr, request.uid
        wizard_obj = request.registry['saas_portal.start_wizard']

        candidates = wizard_obj.search(cr, SUPERUSER_ID,
                                       [("dbname", "=", post["dbname"])])
        wz_id = candidates and candidates[0]
        if not wz_id:
            wz_id = wizard_obj.create(cr, SUPERUSER_ID, post)
            wz = wizard_obj.browse(cr, SUPERUSER_ID, wz_id)
            wz.set_user_id(uid)
        else:
            wz = wizard_obj.browse(cr, SUPERUSER_ID, wz_id)

        if wz.done:
            raise ValueError("DB name not valid")

        state = {
            "wz": wz,
            "wizard_page": PAGE_PLAN_SELECT,
            "meta": self.__get_metadata(wz)
        }
        state.update(self.__get_plans())

        return request.website.render("saas_portal_start_wizard.wizard_tpl",
                                      state)

    def __process_submit(self, wz, post):
        cr, uid = request.cr, SUPERUSER_ID
        plan_model = request.registry['saas_portal.plan']
        user_model = request.registry['res.users']

        errors = dict()
        errors["general"] = []

        partner = user_model.browse(cr, SUPERUSER_ID, request.uid).partner_id

        if post.get("plan_id", False):
            wz.plan_id = int(post["plan_id"])
            plan = plan_model.browse(cr, SUPERUSER_ID, wz.plan_id)

            if getattr(plan, 'pricing', False):
                if not partner.customer:
                    errors["general"].append(
                        "User must be costumer to purchase this plan.")
                    errors['plan_id'] = 'has-error'

        if post.get("name"):
            partner_data = {
                "name": post.get("name"),
                "vat": post.get("vat"),
                "phone": post.get("phone"),
                "city": post.get("city"),
                "state_id": post.get("state_id", False),
                "country_id": post.get("country_id"),
                "zip": post.get("zip_"),
            }
            partner.write(partner_data)

            company_partner = partner.company_id.partner_id
            company_data = {
                "name": post.get("company"),
                "vat": post.get("vat"),
            }
            company_partner.write(company_data)

            wz.set_user_id(request.uid)

        return errors

    @http.route(['/page/start/wizard/submit'], type='http', auth="user",
                website=True)
    def wizard_submit(self, **post):
        cr, uid = request.cr, request.uid
        wizard_obj = request.registry["saas_portal.start_wizard"]
        wz = wizard_obj.browse(cr, SUPERUSER_ID, int(post["wizard_id"]))

        current_page = post.get("wizard_page")
        action = post.get("wizard_action", "next")

        upstream = post.copy()
        # state = {"upstream": upstream.items()}
        state = {}

        errors = self.__process_submit(wz, upstream)
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
        data = False
        while not data:
            _logger.info("\n\nObtaining data for [page: %s]\n", next_page)
            data = {
                PAGE_PLAN_SELECT: self.__get_plans,
                PAGE_TERMS_CONDS: self.__get_terms,
                PAGE_PLAN_CONFIRM: self.__get_legal,
                PAGE_PAYMENT: self.__get_payment_methods,
                PAGE_ADDONS_SELECT: self.__get_addons,
            }[next_page](wz)
            if not data:
                next_page = WIZARD_FLOW[next_page][action]

        # state = {"upstream": upstream.items()}
        state.update(data)
        state.update({"meta": self.__get_metadata(wz), "wizard_page": next_page,
                      "wz": wz})
        _logger.info("\n\nState:: %s\n", state)
        return request.website.render("saas_portal_start_wizard.wizard_tpl",
                                      state)

    @http.route(['/page/start/wizard/payment_cb'], type='http', auth="user",
                website=True)
    def wizard_payment_cb(self, **post):
        _logger.info("\n\nReceived payment with [POST: %s]\n", post)
        cr, uid = request.cr, request.uid
        wizard_obj = request.registry["saas_portal.start_wizard"]
        sale_order_obj = request.registry["sale.order"]

        candidates = wizard_obj.search(cr, SUPERUSER_ID,
                                       [("dbname", "=", post["d"])])
        wz_id = candidates and candidates[0]
        if not wz_id:
            raise ValueError()
        wz = wizard_obj.browse(cr, SUPERUSER_ID, wz_id)
        order = sale_order_obj.browse(cr, SUPERUSER_ID, wz.order_id)

        redirect = "/page/start/wizard/submit?{}".format(werkzeug.url_encode({
            "wizard_page": PAGE_TERMS_CONDS,
            "wizard_action": "next",
            "wizard_id": wz_id
        }))

        sp = SaasPricing()
        return sp.payment_validate(order.id, **{"r": redirect, "plan_id": wz.plan_id})

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

