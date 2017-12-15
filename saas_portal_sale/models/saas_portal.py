# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    free_subdomains = fields.Boolean(help='allow to choose subdomains for trials otherwise allow only after payment', default=True)
    non_trial_instances = fields.Selection([('from_trial', 'From trial'), ('create_new', 'Create new')], string='Non-trial instances',
                                           help='Whether to use trial database or create new one when user make payment', required=True, default='create_new')
    product_tmpl_id = fields.Many2one('product.template', 'Product')

    product_variant_ids = fields.One2many('product.product', 'saas_plan_id', 'Product variants')

    def _prepare_contract(self, name, partner_id, product_id=None):
        res = {
            'name': name,
            'partner_id': partner_id,
            'recurring_invoices': True,
        }

        if product_id:
            product = self.env['product.product'].browse(product_id)
            partner = self.env['res.partner'].browse(partner_id)
            pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
            res.update({
                'pricelist_id': partner.property_product_pricelist and partner.property_product_pricelist.id or False,
                'recurring_invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'name': product.name_get()[0][1],
                    'price_unit': partner.property_product_pricelist and product.with_context(pricelist=partner.property_product_pricelist.id).price or 0.0,
                    'uom_id': product.uom_id.id,
                })],
            })

        return res

    @api.multi
    def _new_database_vals(self, vals):
        vals = super(SaasPortalPlan, self)._new_database_vals(vals)

        product_id = vals.get('product_id')
        contract_vals = self._prepare_contract(vals['name'], vals['partner_id'], product_id=product_id)

        contract = self.env['account.analytic.account'].sudo().create(contract_vals)

        if product_id:
            contract.cron_recurring_create_invoice()  # create invoice for new database immediately

        vals['contract_id'] = contract.id
        return vals


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract',
        readonly=True,
    )
