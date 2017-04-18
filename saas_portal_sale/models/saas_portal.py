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

    invoice_lines = fields.One2many('account.invoice.line', 'saas_portal_client_id')
    trial = fields.Boolean('Trial', help='indication of trial clients', compute='_compute_period_paid', store=True)
    period_paid = fields.Integer('Paid days',
                                 help='Subsription days that were paid',
                                 compute='_compute_period_paid',
                                 store=True)
    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract',
        readonly=True,
    )

    @api.multi
    @api.depends('invoice_lines.invoice_id.state')
    def _compute_period_paid(self):
        for client_obj in self:
            client_obj.expiration_datetime = datetime.strptime(client_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=client_obj.plan_id.expiration)  # for trial
            days = 0
            for line in self.env['account.invoice.line'].search([('saas_portal_client_id', '=', client_obj.id), ('invoice_id.state', '=', 'paid')]):
                days += line.period * line.quantity
            if days != 0:
                client_obj.period_paid = days
            client_obj.trial = not bool(days)

    @api.multi
    def get_upgrade_database_payload(self):
        res = super(SaasPortalClient, self).get_upgrade_database_payload()

        res['params'].append({'key': 'saas_client.trial', 'value': 'False', 'hidden': True})

        if self.invoice_lines:
            params = []
            recent_invoice_line = self.invoice_lines.sorted(reverse=True, key=lambda r: r.create_date)[0]
            product_obj = recent_invoice_line.product_id

            attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'MAX_USERS')
            if attribute_value_obj and attribute_value_obj[0].saas_code_value:
                params.append({'key': 'saas_client.max_users', 'value': attribute_value_obj[0].saas_code_value, 'hidden': True})

            attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'INSTALL_MODULES')
            addons = attribute_value_obj and attribute_value_obj[0].saas_code_value or ''
            if addons:
                res.update({'install_addons': addons.split(',') if addons else []})

            attribute_value_obj = product_obj.attribute_value_ids.filtered(lambda r: r.attribute_id.saas_code == 'STORAGE_LIMIT')
            if attribute_value_obj and attribute_value_obj[0].saas_code_value:
                params.append({'key': 'saas_client.total_storage_limit', 'value': attribute_value_obj[0].saas_code_value, 'hidden': True})

            res['params'].extend(params)
        return res
