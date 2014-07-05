{
    'name' : 'OAuth2 provider (server)',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'Base',
    'website' : 'https://it-projects.info',
    'sequence': 1,

    'depends' : ['web'],
    'data':[],
    'installable': True,

    'description': '''
Addon allows to customers to login in their databases via res_users records in your main database

Depends on https://github.com/idan/oauthlib

Basic flow:

Open url1 at master server from child database:

    import urllib

    url1 = '/oauth2/auth?%s'%urllib.urlencode({
        'state': {"p": 1, "r": "%2Fweb%2Flogin%3F", "d": "some-test-3"},
        'redirect_uri': 'http://odoo.example.com/auth_oauth/signin',
        'response_type': 'token',
        'client_id': 'f23514a1-13a2-40e5-9033-5018e7f3a052',
        'debug': True,
        'scope': 'userinfo'
        })

    print url1

then user inter login-password

then master back:

    http://odoo.example.com/auth_oauth/signin#access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM&token_type=Bearer&state=%7B%27p%27%3A+1%2C+%27r%27%3A+%27%252Fweb%252Flogin%253F%27%2C+%27d%27%3A+%27some-test-3%27%7D&expires_in=3600&scope=userinfo

then client redirect to itself (see @fragment_to_query_string in auth_oauth module)

    http://odoo.example.com/auth_oauth/signin?access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM&token_type=Bearer&state=%7B%27p%27%3A+1%2C+%27r%27%3A+%27%252Fweb%252Flogin%253F%27%2C+%27d%27%3A+%27some-test-3%27%7D&expires_in=3600&scope=userinfo

then client make request to master:

    /oauth2/tokeninfo?access_token=ksESez4jRUxg0v6Kt7HkE5Z4ZtyrrM
    ''',
}
