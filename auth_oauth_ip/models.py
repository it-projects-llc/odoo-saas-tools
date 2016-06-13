import re
import werkzeug
import urllib2
import json
import urlparse

from openerp import models, fields

class auth_oauth_provider(models.Model):

    _inherit = 'auth.oauth.provider'

    local_ip = fields.Char('Local IP', help='Address to be used in server-wide requests')
    local_port = fields.Char('Local Port', help='Address to be used in server-wide requests')


class res_users(models.Model):

    _inherit = 'res.users'

    def _auth_oauth_rpc(self, cr, uid, endpoint, access_token, context=None, local_ip=None, local_port=None):
        params = werkzeug.url_encode({'access_token': access_token})
        host = None
        try:
            host = re.match(".*//([^/]*)/", endpoint).group(1)
        except:
            pass

        if not (host and local_ip and local_port):
            return super(res_users, self)._auth_oauth_rpc(cr, uid, endpoint, access_token, context=context)

        endpoint = endpoint.replace(host, '%s:%s' % (local_ip, local_port))
        if urlparse.urlparse(endpoint)[4]:
            url = endpoint + '&' + params
        else:
            url = endpoint + '?' + params
        req = urllib2.Request(url, headers={'host': host})
        print 'url', url
        # f = urllib2.urlopen(url)
        f = urllib2.urlopen(req)

        response = f.read()
        return json.loads(response)

    def _auth_oauth_validate(self, cr, uid, provider, access_token, context=None):
        """ return the validation data corresponding to the access token """
        p = self.pool.get('auth.oauth.provider').browse(cr, uid, provider, context=context)
        validation = self._auth_oauth_rpc(cr, uid, p.validation_endpoint, access_token, context=context, local_ip=p.local_ip, local_port=p.local_port)
        if validation.get("error"):
            raise Exception(validation['error'])
        if p.data_endpoint:
            data = self._auth_oauth_rpc(cr, uid, p.data_endpoint, access_token, context=context, local_ip=p.local_ip, local_port=p.local_port)
            validation.update(data)
        return validation
