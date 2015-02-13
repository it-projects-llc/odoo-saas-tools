from openerp import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_oauth_validate(self, cr, uid, provider, access_token, context=None):
        validation = super(ResUsers, self)._auth_oauth_validate(cr, uid, provider, access_token, context=None)
        client_id = validation.get('client_id')
        if client_id:
            p = self.pool['auth.oauth.provider'].browse(cr, uid, provider, context=context)
            assert client_id == p.client_id, "wrong client_id"
        return validation
