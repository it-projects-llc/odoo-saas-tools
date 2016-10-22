# -*- coding: utf-8 -*-
import logging
import simplejson
import traceback

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
import werkzeug

_logger = logging.getLogger(__name__)

from ..validators import server

try:
    from oauthlib.oauth2.rfc6749 import errors
    from oauthlib.common import urlencode, urlencoded, quote
except:
    pass
from urlparse import urlparse
from urlparse import urlunparse


# see https://oauthlib.readthedocs.org/en/latest/oauth2/server.html
class OAuth2(http.Controller):

    def __init__(self):
        self._server = server

    def _get_escaped_full_path(self, request):
        """
        Django considers "safe" some characters that aren't so for oauthlib. We have to search for
        them and properly escape.
        TODO: is it correct for odoo?
        """
        parsed = list(urlparse(request.httprequest.path))
        unsafe = set(c for c in parsed[4]).difference(urlencoded)
        for c in unsafe:
            parsed[4] = parsed[4].replace(c, quote(c, safe=''))

        return urlunparse(parsed)

    def _extract_params(self, request, post_dict):
        """
        Extract parameters from the Django request object. Such parameters will then be passed to
        OAuthLib to build its own Request object
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.httprequest.method

        headers = dict(request.httprequest.headers.items())
        if 'wsgi.input' in headers:
            del headers['wsgi.input']
        if 'wsgi.errors' in headers:
            del headers['wsgi.errors']
        if 'HTTP_AUTHORIZATION' in headers:
            headers['Authorization'] = headers['HTTP_AUTHORIZATION']
        body = urlencode(post_dict.items())
        return uri, http_method, body, headers

    def _response_from_error(self, e):
        _logger.info("\n%s", traceback.format_exc())
        return 'Error (TODO)'

    def _response(self, headers, body, status=200):
        try:
            fixed_headers = {str(k): v for k, v in headers.items()}
        except:
            fixed_headers = headers
        response = werkzeug.Response(response=body, status=status, headers=fixed_headers)
        return response

    @http.route('/oauth2/auth', type='http', auth='public')
    def auth(self, **kw):
        # kw:
        #
        # state: {"p": 1, "r": "%2Fweb%2Flogin%3F", "d": "some-test-3"}
        # redirect_uri: https://example.odoo.com/auth_oauth/signin
        # response_type: token
        # client_id: d885dde2-0168-4650-9a32-ceb058e652a2
        # debug: False
        # scope: userinfo
        uri, http_method, body, headers = self._extract_params(request, kw)
        user = self.get_user(kw)

        try:
            scopes, credentials = self._server.validate_authorization_request(
                uri, http_method, body, headers)
        # Errors that should be shown to the user on the provider website
        except errors.FatalClientError as e:
            return self._response_from_error(e)
        # Errors embedded in the redirect URI back to the client
        except errors.OAuth2Error as e:
            return self._response({'Location': e.redirect_uri}, None, 302)

        if user.login == 'public':
            scope = kw.get('scope')
            params = {'mode': 'login',
                      'scope': scope,
                      # 'debug':1,
                      # 'login':?,
                      # 'redirect_hostname':TODO,
                      'redirect': '/oauth2/auth?%s' % werkzeug.url_encode(kw)
                      }
            url = '/web/login'
            if 'trial' in scope.split(' '):
                url = '/web/signup'
            return self._response({'Location': '{url}?{params}'.format(url=url, params=werkzeug.url_encode(params))}, None, 302)
        else:
            credentials.update({'user': user})
            try:
                headers, body, status = self._server.create_authorization_response(
                    uri, http_method, body, headers, scopes, credentials)
                return self._response(headers, body, status)
            except errors.FatalClientError as e:
                return self._response_from_error(e)

    @http.route('/oauth2/tokeninfo', type='http', auth='public')
    def tokeninfo(self, **kw):
        uri, http_method, body, headers = self._extract_params(request, kw)
        is_valid, req = self._server.verify_request(uri, http_method, body,
                                                    headers)
        headers = None
        body = simplejson.dumps({'user_id': req.user.id,
                                 'client_id': req.client.client_id,
                                 'email': req.user.email,
                                 'name': req.user.name})
        status = 200
        return self._response(headers, body, status)

    def get_user(self, kw):
        user_obj = request.env['res.users'].sudo()
        uid = kw.get('uid', False) or request.uid
        return user_obj.browse(int(uid))
