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

    @api.multi
    def _new_database_vals(self, vals):
        vals = super(SaasPortalPlan, self)._new_database_vals(vals)
        product = self.product_tmpl_id.product_variant_ids[0]
        partner = self.env['res.partner'].browse(vals['partner_id'])
        pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
        contract = self.env['account.analytic.account'].sudo().create({
            'name': vals['name'],
            'partner_id': vals['partner_id'],
            'recurring_invoices': True,
            'pricelist_id': partner.property_product_pricelist and partner.property_product_pricelist.id or False,
            'recurring_invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': product.name_get()[0][1],
                'price_unit': partner.property_product_pricelist and product.with_context(pricelist=partner.property_product_pricelist.id).price or 0.0,
                'uom_id': product.uom_id.id,
            })],
        })
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
