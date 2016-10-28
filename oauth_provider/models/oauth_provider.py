# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

try:
    from oauthlib import common as oauthlib_common
except:
    pass

import uuid


class OauthApplication(models.Model):
    CLIENT_ID_CHARACTER_SET = r'_-.:;=?!@0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    _name = 'oauth.application'
    _rec_name = 'client_id'

    def generate_client_id(self):
        return str(uuid.uuid1())

    client_id = fields.Char('Client ID', index=True, required=True, default=generate_client_id)
    token_ids = fields.One2many('oauth.access_token', 'application_id', 'Tokens')

    _sql_constraints = [
        ('client_id_uniq', 'unique (client_id)', 'client_id should be unique!'),
    ]

    @api.multi
    def _get_access_token(self, user_id=None, create=False):
        self.ensure_one()
        if not user_id:
            user_id = self.env.user.id

        access_token = self.env['oauth.access_token'].sudo().search([('application_id', '=', self.id), ('user_id', '=', user_id)], order='id DESC', limit=1)
        if access_token:
            access_token = access_token[0]
            if access_token.is_expired():
                access_token = None
        if not access_token and create:
            expires = datetime.now() + timedelta(seconds=60 * 60)
            vals = {
                'user_id': user_id,
                'scope': 'userinfo',
                'expires': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'token': oauthlib_common.generate_token(),
                'application_id': self.id,
            }
            access_token = self.env['oauth.access_token'].create(vals)
            # we have to commit now, because /oauth2/tokeninfo could
            # be called before we finish current transaction.
            self._cr.commit()
        if not access_token:
            return None
        return access_token.token


class OauthAccessToken(models.Model):
    _name = 'oauth.access_token'

    application_id = fields.Many2one('oauth.application', string='Application')
    token = fields.Char('Access Token', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    expires = fields.Datetime('Expires', required=True)
    scope = fields.Char('Scope')

    @api.multi
    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        self.ensure_one()
        return not self.is_expired() and self._allow_scopes(scopes)

    @api.multi
    def is_expired(self):
        self.ensure_one()
        return datetime.now() > datetime.strptime(self.expires, DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def _allow_scopes(self, scopes):
        self.ensure_one()
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)
