import re
import werkzeug
import urllib.request
import urllib.error
import urllib.parse
import json

from odoo import models, fields, api


class auth_oauth_provider(models.Model):

    _inherit = 'auth.oauth.provider'

    local_host = fields.Char(
        'Local IP', help='Address to be used in server-wide requests')
    local_port = fields.Char(
        'Local Port', help='Address to be used in server-wide requests')


class res_users(models.Model):

    _inherit = 'res.users'

    def _auth_oauth_rpc(self, endpoint, access_token, local_host=None, local_port=None):
        params = werkzeug.url_encode({'access_token': access_token})
        host = None
        try:
            host = re.match(".*//([^/]*)/", endpoint).group(1)
        except Exception as e:
            pass

        if not (host and local_host and local_port):
            return super(res_users, self)._auth_oauth_rpc(endpoint, access_token)

        endpoint = endpoint.replace(host, '%s:%s' % (local_host, local_port))
        if urllib.parse.urlparse(endpoint)[4]:
            url = endpoint + '&' + params
        else:
            url = endpoint + '?' + params
        req = urllib.request.Request(url, headers={'host': host})
        print(('url', url))

        with urllib.request.urlopen(req) as response:
            html = response.read()
            return json.loads(html.decode("utf-8"))

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        p = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(
            p.validation_endpoint, access_token, local_host=p.local_host, local_port=p.local_port)
        if validation.get("error"):
            raise Exception(validation['error'])
        if p.data_endpoint:
            data = self._auth_oauth_rpc(
                p.data_endpoint, access_token, local_host=p.local_host, local_port=p.local_port)
            validation.update(data)
        return validation
