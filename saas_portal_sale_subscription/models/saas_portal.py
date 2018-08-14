from datetime import timedelta
from odoo import api, fields, models, _


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    def create_new_database(self, **kwargs):
        '''
        If there is an invoice line for the customer and the plan that has no
        client then start client subscription with this invoice line
        '''
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)

        partner_id = kwargs.get('partner_id')
        trial = kwargs.get('trial')
        if not partner_id:
            return res
        if trial:
            return res
        client = self.env['saas_portal.client'].browse(res.get('id'))

        subscription_wizard_obj = self.env['saas_portal.subscription_wizard']
        invoice_lines = subscription_wizard_obj._get_invoice_lines_wo_client(
            partner_id=partner_id, plan_id=self.id)
        if invoice_lines:
            client.start_subscription(invoice_lines[0].id)

        payload = client.get_upgrade_database_payload()
        self.env['saas.config'].do_upgrade_database(payload, client)

        return res


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    invoice_line_ids = fields.One2many(
        'account.invoice.line', 'saas_client_id', 'Invoice lines',
        readonly=True)
    period_paid = fields.Integer(
        'Period paid', compute='_compute_period_paid', store=True)
    subscription_start = fields.Datetime(
        'Subscription start', track_visibility='onchange', readonly=True)
    trial = fields.Boolean(
        'Trial', compute='_compute_period_paid', store=True)

    @api.multi
    @api.depends('create_date', 'period_paid', 'subscription_log_ids',
                 'subscription_start', 'trial')
    def _compute_expiration(self):
        for record in self:
            start = record.subscription_start or record.create_date
            expiration = (
                fields.Datetime.from_string(start) +
                timedelta(record.period_paid) +
                record.get_subscription_log_timedelta() +
                timedelta(record.plan_id.grace_period)
            )
            if record.trial:
                expiration += timedelta(hours=record.plan_id.expiration)
            record.expiration_datetime = fields.Datetime.to_string(expiration)

    @api.multi
    @api.depends('invoice_line_ids.invoice_id.state')
    def _compute_period_paid(self):
        for client in self:
            period_paid = 0
            for line in client.invoice_line_ids:
                if line.invoice_id.state == 'paid':
                    period_paid += (line.saas_subscription_period *
                                    line.quantity)
            client.period_paid = period_paid
            client.trial = period_paid <= 0

    @api.multi
    def get_upgrade_database_payload(self):
        res = super(SaasPortalClient, self).get_upgrade_database_payload()

        res['params'].append({
            'key': 'saas_client.trial',
            'value': 'False',
            'hidden': True,
        })

        if self.invoice_line_ids:
            last_invoice_line = self.invoice_line_ids.sorted(
                key=lambda l: l.create_date, reverse=True)[0]
            product = last_invoice_line.product_id

            attr_vals = product.attribute_value_ids.filtered(
                lambda v: v.attribute_id.saas_code == 'max_users')
            if attr_vals and attr_vals[0].saas_code_value:
                res['params'].append({
                    'key': 'saas_client.max_users',
                    'value': attr_vals[0].saas_code_value,
                    'hidden': True,
                })

            attr_vals = product.attribute_value_ids.filtered(
                lambda v: v.attribute_id.saas_code == 'install_modules')
            if attr_vals and attr_vals[0].saas_code_value:
                res['install_addons'] = attr_vals[0].saas_code_value.split(',')

            attr_vals = product.attribute_value_ids.filtered(
                lambda v: v.attribute_id.saas_code == 'total_storage_limit')
            if attr_vals and attr_vals[0].saas_code_value:
                res['params'].append({
                    'key': 'saas_client.total_storage_limit',
                    'value': attr_vals[0].saas_code_value,
                    'hidden': True,
                })

        return res

    @api.one
    def start_subscription(self, invoice_line_id):
        # start subscription and relate client with invoice line
        self.write({
            'subscription_start': fields.Datetime.now(),
            'invoice_line_ids': [(6, 0, [invoice_line_id])],
        })
        if not self.contract_id:
            return
        invoice_line = self.env['account.invoice.line'].browse(invoice_line_id)
        # relate invoice with contract
        invoice_line.invoice_id.contract_id = self.contract_id.id
        invoice_line.account_analytic_id = self.contract_id.id
        # prepare contract from invoice line
        recurring_interval = invoice_line.saas_subscription_period
        date_start = fields.Date.today()
        recurring_next_date = fields.Date.to_string(
            fields.Date.from_string(date_start) +
            timedelta(invoice_line.quantity * recurring_interval))
        recurring_name = '%s\n%s' % (
            invoice_line.product_id.display_name,
            _('From #START# to #END#'))
        self.contract_id.write({
            'recurring_invoices': True,
            'recurring_interval': recurring_interval,
            'recurring_rule_type': 'daily',
            'date_start': date_start,
            'recurring_next_date': recurring_next_date,
            'recurring_invoice_line_ids': [(0, 0, {
                'product_id': invoice_line.product_id.id,
                'name': recurring_name,
                'quantity': 1,
                'uom_id': invoice_line.product_id.uom_id.id,
                'automatic_price': False,
                'price_unit': invoice_line.price_unit,
            })],
        })
