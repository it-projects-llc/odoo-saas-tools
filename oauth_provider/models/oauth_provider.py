# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import SUPERUSER_ID
from datetime import datetime
from oauthlib.common import generate_client_id as oauthlib_generate_client_id
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class oauth_application(osv.Model):
    CLIENT_ID_CHARACTER_SET = r'_-.:;=?!@0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    _name = 'oauth.application'
    _columns = {
        'name': fields.char('Database name', readonly=True),
        'client_id' : fields.char('Client ID', readonly=True, select=True, required=True),
        'token_ids': fields.one2many('oauth.access_token', 'application_id', 'Tokens'),
        'user_ids': fields.related('token_ids', 'user_id', readonly=True, type='one2many', relation='res.users', string='Users'),

        #user = models.ForeignKey(AUTH_USER_MODEL, related_name="%(app_label)s_%(class)s")
        #help_text = _("Allowed URIs list, space separated")
        #redirect_uris = models.TextField(help_text=help_text,
        #                                 validators=[validate_uris], blank=True)
        #client_type = models.CharField(max_length=32, choices=CLIENT_TYPES)
        #authorization_grant_type = models.CharField(max_length=32,
        #                                            choices=GRANT_TYPES)
        #client_secret = models.CharField(max_length=255, blank=True,
        #                                 default=generate_client_secret, db_index=True)
        #name = models.CharField(max_length=255, blank=True)

    }
    _defaults = {
        #'client_secret': lambda self,cr,uid,ctx={}: oauthlib_generate_client_id(length=128, chars=CLIENT_ID_CHARACTER_SET)
    }

#class oauth_grant(osv.Model):
#    _name = 'oauth.access_token'
#    _columns = {
#        'application_id':fields.many2one('oauth.application', string='Application')
#        'user_id':fields.many2one('res.users', string='User'),
#        'code':fields.char('Code')
#        'expires':fields.datetime('Expires'),
#        'redirect_uri':fields.char('Redirect uri')
#        'scope':fields.char('Scope')
#    }

class oauth_access_token(osv.Model):
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
        
#class oauth_refresh_token(osv.Model):
#    _name = 'oauth.refresh_token'
#    _columns = {
#        'application_id':fields.many2one('oauth.application', string='Application')
#        'token' : fields.char('Access Token'),
#        'user_id':fields.many2one('res.users', string='User'),
#        'access_token_id':fields.many2one('oauth.access_token', string='Access token'),
#    }


