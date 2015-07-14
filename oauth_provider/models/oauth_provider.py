# -*- coding: utf-8 -*-
from openerp import models, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

import uuid

class OauthApplication(models.Model):
    CLIENT_ID_CHARACTER_SET = r'_-.:;=?!@0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    _name = 'oauth.application'

    def generate_client_id(self):
        return str(uuid.uuid1())

    name = fields.Char('Database name', readonly=True)
    client_id = fields.Char('Client ID', readonly=True, select=True, required=True, default=generate_client_id)
    token_ids = fields.One2many('oauth.access_token', 'application_id', 'Tokens')

class OauthAccessToken(models.Model):
    _name = 'oauth.access_token'
    _columns = {
        'application_id':fields.many2one('oauth.application', string='Application'),
        'token' : fields.char('Access Token', required=True),
        'user_id':fields.many2one('res.users', string='User', required=True),
        'expires':fields.datetime('Expires', required=True),
        'scope':fields.char('Scope'),
    }
    def is_valid(self, cr, uid, ids, scopes=None, context=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        res = {}
        for t in self.browse(cr, uid, ids, context=context):
            res[t.id] = datetime.now() >= datetime.strptime(t.expires, DEFAULT_SERVER_DATETIME_FORMAT) and self._allow_scopes(cr, uid, t, scopes)
        return res

    def is_expired(self, cr, uid, ids, context=None):
        res = {}
        for t in self.browse(cr, uid, ids, context=context):
            res[t.id] = datetime.now() >= self.expires
        return res

    def _allow_scopes(self, cr, uid, token, scopes, context=None):
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)

    def allow_scopes(self, cr, uid, ids, scopes, context=None):
        """
        Check if the token allows the provided scopes

        :param scopes: An iterable containing the scopes to check
        """
        res = {}
        for t in self.browse(cr, uid, ids, context=context):
            res[t.id] = self._allow_scopes(cr, uid, t, scopes, context=context)
        return res
