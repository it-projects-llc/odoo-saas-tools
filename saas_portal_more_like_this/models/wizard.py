# -*- coding: utf-8 -*-
import requests
import werkzeug
import datetime
import simplejson

import openerp
from openerp.addons.saas_utils import connector, database
from openerp.addons.web.http import request
from openerp.tools import config
from openerp import models, fields, api, SUPERUSER_ID
from openerp import http


class SaasPortalDuplicateClient(models.TransientModel):
    _name = 'saas_portal.duplicate_client'

    def _default_client_id(self):
        return self._context.get('active_id')

    def _default_partner(self):
        client_id = self._default_client_id()
        if client_id:
            client = self.env['saas_portal.client'].browse(client_id)
            return client.partner_id
        return ''
    
    def _default_expiration(self):
        client_id = self._default_client_id()
        if client_id:
            client = self.env['saas_portal.client'].browse(client_id)
            return client.plan_id.expiration
        return ''

    name = fields.Char('Database Name', required=True)
    client_id = fields.Many2one('saas_portal.client', string='Base Client', readonly=True, default=_default_client_id)
    expiration = fields.Integer('Expiration', default=_default_expiration)
    partner_id = fields.Many2one('res.partner', string='Partner', default=_default_partner)

    @api.multi
    def apply(self):
        wizard = self[0]
        url = wizard.client_id.duplicate_database(dbname=wizard.name, partner_id=wizard.partner_id.id, expiration=None)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Duplicate Client',
            'url': url
        }
