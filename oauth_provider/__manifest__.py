# -*- coding: utf-8 -*-
{
    'name': 'OAuth2 provider',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'https://it-projects.info',

    'depends': ['web'],
    'external_dependencies': {
        'python': ['oauthlib'],
    },
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,

    'description': '''
Addon allows to users to login in odoo databases via master database

INSTALLATION
============

Dependencies
------------

* https://github.com/idan/oauthlib

Basic flow
==========

Terms
-----

* User -- a human
* Master -- an odoo database where this module is installed
* Client -- an odoo database where you need to authenticate user and where module auth_oauth module is installed


Steps
-----

From client database redirects user to url1 at master database:

    import urllib

    url1 = '/oauth2/auth?%s' % urllib.urlencode({

    'state': {"p": 1, "r": "%2Fweb%2Flogin%3F", "d": "client_database"},

    'redirect_uri': 'http://odoo.example.com/auth_oauth/signin',

    'response_type': 'token',

    'client_id': 'f23514a1-13a2-40e5-9033-5018e7f3a052',

    'debug': False,

    'scope': 'userinfo'

    })

    print url1

if user is not logined at master:

* master redirects user to /web/login page
* user enters login-password
* master redirects user to url1

then master redirects user back:

    http://odoo.example.com/auth_oauth/signin#access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM&token_type=Bearer&state=%7B%27p%27%3A+1%2C+%27r%27%3A+%27%252Fweb%252Flogin%253F%27%2C+%27d%27%3A+%27some-test-3%27%7D&expires_in=3600&scope=userinfo

then client redirects user to itself (see @fragment_to_query_string in auth_oauth module)

    http://odoo.example.com/auth_oauth/signin?access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM&token_type=Bearer&state=%7B%27p%27%3A+1%2C+%27r%27%3A+%27%252Fweb%252Flogin%253F%27%2C+%27d%27%3A+%27some-test-3%27%7D&expires_in=3600&scope=userinfo

then client make request to master:

    /oauth2/tokeninfo?access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM

and master returns user data:

    {"user_id": 3, "email": "admin@example.com", "name": "Administrator"}

    ''',
}
