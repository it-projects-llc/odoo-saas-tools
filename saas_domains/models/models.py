# -*- coding: utf-8 -*-

from odoo import api, models, fields


class SaasDomainZone(models.Model):
    _name = 'saas_sysadmin.domain.zone'

    name = fields.Char('Domain', required=True)
    soa_email = fields.Char('SOA Email', required=True)
    a_record_ids = fields.One2many('saas_sysadmin.domain.record', 'zone_id', 'A/AAA Records')
    dns_provider = fields.Selection(
        [
            ('route53', 'AWS Route53'),
            ('linode', 'Linode')
        ],
        string='DNS Provider',
        required=True,
        default='route53'
    )

    @api.multi
    def action_pull_records(self):
        raise NotImplementedError

    @api.multi
    def action_push_records(self):
        raise NotImplementedError


class SaasDomainRecord(models.Model):
    _name = 'saas_sysadmin.domain.record'

    hostname = fields.Char('Hostname', required=True)
    ttl_value = fields.Char('TTL')
    type = fields.Selection(
        [
            ('ns', 'NS'),
            ('mx', 'MX'),
            ('a', 'A/AAA'),
            ('cname', 'CNAME'),
            ('txt', 'TXT')
        ],
        required=True,
        default='a'
    )
    ip_address = fields.Char('IP Address')
    zone_id = fields.Many2one(comodel_name='saas_sysadmin.domain.zone', string='Zone', ondelete='cascade')
    auto_sync = fields.Boolean('Auto Sync with Provider (CRUD)')

    @api.multi
    def action_sync(self, method='POST'):
        """
        based on method will call API
        """
        raise NotImplementedError

    @api.model
    def create(self, values):
        record = super(SaasDomainRecord, self).create(values)
        if record.auto_sync:
            self.action_sync()
        return record

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.auto_sync:
                self.action_sync('DELETE')
        return True
