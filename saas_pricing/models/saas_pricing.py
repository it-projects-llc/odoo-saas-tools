# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api

from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


USERS = "users"
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
        _logger.info("\n\nENTRIES: %s\n", entries)
        for entry in entries:
            if not entry:
                continue

            base, price = entry.split("*")
            base = base.split(">")
            id_ = base.pop(0)
            min_ = False
            if id_.startswith("("):
                id_ = id_[1:]

            if not id_ in VARIABLE_INDICATORS.keys():
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
        _logger.info(values)

        rc = super(SaasPricingPrice, self).create(values)

        # if rc:
        #     rc.create_services()

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
        _logger.info("\n\nCandidates SO: %s\n", candidates)

        if candidates:
            if len(candidates) > 1:
                _logger.error("More than 1 order for the period .. not good: %s", candidates)
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

            _logger.info("\n\nBasePrice: %s\n", base_priced.list_price)
            if base_priced and base_priced.list_price > 0:
                order_lines.append((0, False, {
                    "product_id": base_priced.id
                }))

            if not tenant_creation and self.pricing.pricing == "variable":
                for p in self.pricing.services:
                    if p.id == base_priced.id:
                        continue
            vals.update({"order_line": order_lines})

            _logger.info("\n\nCreating order with vals: %s\n", vals)

            order = so_model.create(vals)

        return order


