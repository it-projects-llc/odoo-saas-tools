# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests

import logging
_logger = logging.getLogger(__name__)


USERS = "users_len"
MODULES = "modules"
FILE_STORAGE = "file_storage"
DB_STORAGE = "db_storage"

VARIABLE_INDICATORS = {
    USERS: "Users count",
    MODULES: "Installed modules",
    FILE_STORAGE: "File Storage used",
    DB_STORAGE: "Database Storage used"
}

SELLER_XMLID = "saas_pricing.plan_supplier_partner"


class SaasPricingPrice(models.Model):
    _name = 'saas_pricing.price'

    name = fields.Char(readonly=True)

    pricing = fields.Selection([
        ('fixed', "Fixed"),
        ('variable', "Variable")
    ], "Pricing", default="fixed", required=True)
    price = fields.Float('Base Price', digits=(16, 2), required=True)
    variable_mode = fields.Char("Pricing expression")

    billing = fields.Selection([
        ('pre', "Pre Paid"),
        ('post', "Post Paid"),
    ], "Billing", default='post', required=True)

    period = fields.Selection([
        ('weekly', "Weekly"),
        ('fortnightly', "Fortnightly"),
        ('monthly', "Monthly"),
        ('quarterly', "Quarterly"),
        ('annually', "Annually"),
        ('custom', "Custom"),
    ], 'Billing period', default='monthly', required=True)
    custom_period = fields.Integer("Custom period length (in days)")

    trial_days = fields.Integer('Trial period (in days)', default=5)
    grace_days = fields.Integer('Grace period (in days)', default=5)
    payment_due_days = fields.Integer("Payment Due Alert (in days)", default=5)
    purge_due_days = fields.Integer("Data Purging (in days)", default=1)

    services = fields.Many2many('product.product', string="Associated services",
                                readonly=True)

    def __get_service_vals(self, name, price, qty=0, supplier_id=False):
        imd = self.env['ir.model.data']
        return {
            "name": name,
            "list_price": float(price),
            "type": "service",
            "state": "sellable",
            "sale_ok": False,
            "seller_ids": [
                (0 if not supplier_id else 1, supplier_id, {
                    "name": imd.xmlid_to_res_id(SELLER_XMLID),
                    "min_qty": qty,
                })
            ]
        }

    def __parse_variable_expression(self, exp):
        data = []
        entries = exp.split(";")

        for entry in entries:
            if not entry:
                continue

            base, price = entry.split("*")
            base = base.split(">")
            id_ = base.pop(0)
            min_ = False
            if id_.startswith("("):
                id_ = id_[1:]

            if id_ not in VARIABLE_INDICATORS.keys():
                continue

            if base:
                min_ = base.pop(0)
                if min_.endswith(")"):
                    min_ = min_[:-1]

            service_name = VARIABLE_INDICATORS[id_]
            if min_:
                service_name = "{} over {}".format(service_name, min_)
            data.append(self.__get_service_vals(service_name, price, min_))

        return data

    @api.model
    def create(self, values):
        name = "{pricing}_{billing}_{period}"
        if values['period'] == 'custom':
            name += "_{custom_period}"
        name += "_{price}"
        name = name.format(**values)
        values.update({"name": name})

        data = []
        if values['price'] > 0:
            price = values['price']
            service_name = "Fixed price Plan"
            data.append(self.__get_service_vals(service_name, price))

        if values['pricing'] == "variable":
            data.extend(
                self.__parse_variable_expression(values['variable_mode']))

        if data:
            values.update({"services": [(0, False, d) for d in data]})

        rc = super(SaasPricingPrice, self).create(values)
        return rc


class SaasPricingPlan(models.Model):
    _inherit = 'saas_portal.plan'
    
    pricing = fields.Many2one('saas_pricing.price', "Pricing")

    @api.one
    def get_sale_order(self, partner_id, tenant_name, force_create=True,
                       tenant_creation=False):
        so_model = self.env['sale.order']
        product_model = self.env['product.product']

        today = datetime.today()

        domain = [
            ("client_order_ref", "=", tenant_name),
            ("partner_id", "=", partner_id),
            ("state", "!=", "cancel"),
        ]

        d = {
            'weekly': {"weeks": 1},
            'fortnightly': {"weeks": 2},
            'monthly': {"months": 1},
            'quarterly': {"months": 3},
            'annually': {"years": 1},
            'custom': {"days": self.pricing.custom_period}
        }

        max_period_start = today - relativedelta(**d[self.pricing.period])

        # if self.pricing.billing == "pre":
        domain.append(
            ('date_order', '>', max_period_start.strftime("%Y-%m-%d"))
        )

        candidates = so_model.search(domain)

        if candidates:
            if len(candidates) > 1:
                _logger.error(
                    "More than 1 order for the period .. not good: %s",
                    candidates)
                return False
            order = candidates[0]
        elif force_create:
            vals = {
                "client_order_ref": tenant_name,
                "partner_id": partner_id,
                "date_order": today,
            }

            order_lines = []
            domain = [("name", "=", "Fixed price Plan"),
                      ('id', 'in', [x.id for x in self.pricing.services])]
            base_priced = product_model.search(domain)

            if base_priced and base_priced.list_price > 0:
                order_lines.append((0, False, {
                    "product_id": base_priced.id
                }))

            if not tenant_creation and self.pricing.pricing == "variable":
                for p in self.pricing.services:
                    if p.id == base_priced.id:
                        continue
            vals.update({"order_line": order_lines})

            order = so_model.create(vals)

        return order

    @api.model
    def action_check_tenants_status(self):
        server_model = self.env['saas_portal.server']
        client_model = self.env['saas_portal.client']

        server_model.action_sync_server_all()

        today = datetime.today()

        domain = [('state', '=', 'open')]
        clients = client_model.search(domain)

        for c in clients:
            if c.expired:
                continue

            plan = c.plan_id
            if not plan.pricing:
                continue

            last_order = c.get_last_sale_order()
            last_order = last_order and last_order[0] or False

            d = {
                'weekly': {"weeks": 1},
                'fortnightly': {"weeks": 2},
                'monthly': {"months": 1},
                'quarterly': {"months": 3},
                'annually': {"years": 1},
                'custom': {"days": plan.pricing.custom_period}
            }
            max_period_start = today - relativedelta(**d[plan.pricing.period])

            if not last_order:
                last_order = c.create_sale_order()
                last_order = last_order and last_order[0]

                last_order.message_post(body="You have unpaid sales order(s)",
                                        partner_ids=[c.partner_id.id])
                last_order.sudo(SUPERUSER_ID).message_subscribe(
                    [c.partner_id.id])

            if last_order.date_order < max_period_start.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT):
                _logger.info("LastOrder is over due")
                if not last_order.invoiced:
                    _logger.info("... and not invoiced")
                    grace_days = max_period_start - relativedelta(
                        days=plan.pricing.grace_days)
                    if last_order.date_order < grace_days.strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT):
                        _logger.info("<Client: %s> is over its grace days",
                                     c.id)
                        last_order.message_post(
                            body="Your tenant '%s' will be purged due to "
                                 "lack of payment." % (c.name,),
                            partner_ids=[c.partner_id.id])
                    else:
                        c.disable_database()
                        last_order.message_post(
                            body="Your tenant '%s' has being disabled due to "
                                 "lack of payment." % (c.name,),
                            partner_ids=[c.partner_id.id])
                else:
                    c.enable_database()
                    last_order.message_post(
                        body="Your tenant '%s' has being enabled." % (c.name,),
                        partner_ids=[c.partner_id.id])

                    last_order = c.create_sale_order()[0]
                    last_order.message_post(
                        body="You have unpaid sales order(s)",
                        partner_ids=[c.partner_id.id])
                    last_order.sudo(SUPERUSER_ID).message_subscribe(
                        [c.partner_id.id])


class SaasPricingClient(models.Model):
    _inherit = 'saas_portal.client'

    @api.one
    def get_last_sale_order(self):
        so_model = self.env['sale.order']
        product_model = self.env['product.product']

        domain = [
            ("partner_id", "=", self.partner_id.id),
            ("state", "!=", "cancel"),
            '|', ("client_order_ref", "=", self.name),
                 ("client_order_ref", "=", self.name.split(".")[0]),
        ]

        candidates = so_model.search(domain)

        # TODO: get a better sorting algorithm... maybe native?
        last_order = False
        for order in candidates:
            if not last_order or (order.date_order > last_order.date_order):
                last_order = order

        return last_order

    @api.one
    def create_sale_order(self):
        so_model = self.env['sale.order']
        product_model = self.env['product.product']

        today = datetime.today()

        vals = {
            "client_order_ref": self.name,
            "partner_id": self.partner_id.id,
            "date_order": today,
        }

        order_lines = []
        services = self.plan_id.pricing.services

        domain = [("name", "=", "Fixed price Plan"),
                  ('id', 'in', [x.id for x in services])]
        base_priced = product_model.search(domain)

        if base_priced and base_priced.list_price > 0:
            order_lines.append((0, False, {
                "product_id": base_priced.id
            }))

        if self.plan_id.pricing.pricing == "variable":
            _items = VARIABLE_INDICATORS.items()
            k = [x[0] for x in _items]
            v = [x[1] for x in _items]
            for s in services:
                if s.id != base_priced.id:
                    indicator, min = s.name.split(" over ")
                    min = int(min)
                    key = k[v.index(indicator)]
                    real = getattr(self, key, 0)
                    billable = (real - min) if (real > min) else 0

                    if billable:
                        order_lines.append((0, False, {
                            "product_id": s.id,
                            "product_uom": billable
                        }))

        vals.update({"order_line": order_lines})
        order = so_model.create(vals)

        return order

    @api.one
    def disable_database(self):
        _logger.info("Requesting server to disable database...")
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }
        url = self.server_id._request_server(
            path="/saas_server/disable_database",
            state=state, client_id=self.client_id)[0]
        rc = requests.get(url, verify=(
            self.server_id.request_scheme == 'https' and
            self.server_id.verify_ssl)
        )
        return rc

    @api.one
    def enable_database(self):
        _logger.info("Requesting server to enable database...")
        state = {
            'd': self.name,
            'client_id': self.client_id,
        }
        url = self.server_id._request_server(
            path="/saas_server/enable_database",
            state=state, client_id=self.client_id)[0]
        rc = requests.get(url, verify=(
            self.server_id.request_scheme == 'https' and
            self.server_id.verify_ssl)
                          )
        return rc
