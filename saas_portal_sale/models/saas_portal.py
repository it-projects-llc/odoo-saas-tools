# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    free_subdomains = fields.Boolean(help='allow to choose subdomains for trials otherwise allow only after payment', default=True)
    non_trial_instances = fields.Selection([('from_trial', 'From trial'), ('create_new', 'Create new')], string='Non-trial instances',
                                           help='Whether to use trial database or create new one when user make payment', required=True, default='create_new')

    @api.multi
    def _new_database_vals(self, vals):
        vals = super(SaasPortalPlan, self)._new_database_vals(vals)
        vals['contract_id'] = self.env['account.analytic.account'].sudo().create({
            'name': vals['name'],
            'partner_id': vals['partner_id'],
            'recurring_invoices': True,
        }).id
        return vals


    @api.multi
    def create_new_database(self, **kwargs):
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)

        partner_id = kwargs.get('partner_id')
        trial = kwargs.get('trial')
        if not partner_id:
            return res
        if trial and self.non_trial_instances != 'from_trial':
            return res

        lines = self.env['saas_portal.subscription_wizard'].find_partner_payments(partner_id=partner_id, plan_id=self.id)
        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        lines.write({'saas_portal_client_id': client_obj.id})

        if not trial:
            client_obj.subscription_start = client_obj.create_date

        payload = client_obj.get_upgrade_database_payload()
        self.env['saas.config'].do_upgrade_database(payload, client_obj)

        return res


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract',
        readonly=True,
    )
