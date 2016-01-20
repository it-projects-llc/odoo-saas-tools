# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def create_new_database(self, dbname=None, client_id=None, partner_id=None, user_id=None, notify_user=False, trial=False, support_team_id=None):
        res = super(SaasPortalPlan, self).create_new_database(dbname=dbname,
                                                              client_id=client_id,
                                                              partner_id=partner_id,
                                                              user_id=user_id,
                                                              notify_user=notify_user,
                                                              trial=trial,
                                                              support_team_id=support_team_id)
        lines = self.env['saas_portal.find_payments_wizard'].find_partner_payments(partner_id=partner_id, plan_id=self.id)

        client_obj = self.env['saas_portal.client'].browse(res.get('id'))
        for l in lines.sorted(key=lambda r: r.create_date):
            if l.product_id.subscription_per_user:
                payload = {'params': [{'key': 'saas_client.max_users', 'value': l.quantity, 'hidden': True}]}
                self.env['saas.config'].do_upgrade_database(payload, client_obj.id)
                break

        if not trial:
            client_obj.subscription_start = client_obj.create_date
        lines.write({'saas_portal_client_id': client_obj.id})
        return res


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    subscription_start = fields.Datetime(string="Subscription start", track_visibility='onchange')
    expiration_datetime = fields.Datetime(string="Expiration", compute='_handle_paid_invoices',
                                          store=True,
                                          help='Subscription start plus all paid days from related invoices')
    invoice_lines = fields.One2many('account.invoice.line', 'saas_portal_client_id')
    trial = fields.Boolean('Trial', help='indication of trial clients', default=False, store=True, readonly=True, compute='_handle_paid_invoices')

    @api.multi
    @api.depends('invoice_lines.invoice_id.state')
    def _handle_paid_invoices(self):
        for client_obj in self:
            client_obj.expiration_datetime = datetime.strptime(client_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=client_obj.plan_id.expiration)  # for trial
            days = 0
            for line in self.env['account.invoice.line'].search([('saas_portal_client_id', '=', client_obj.id), ('invoice_id.state', '=', 'paid')]):
                days += line.product_id.period
            if days != 0:
                client_obj.expiration_datetime = datetime.strptime(client_obj.subscription_start or client_obj.create_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=days)
            client_obj.trial = not bool(days)
