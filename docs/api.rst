API integration
===============

To control SaaS via external tool `built-in XML-RPC <https://www.odoo.com/documentation/8.0/api_integration.html>`__ can be used.

Example in python language
--------------------------

::

    # Import libs
    import json
    import xmlrpclib
    import requests

    # Define credentials
    main_url = 'http://odoo.local'
    main_db = 'odoo.local'
    admin_username = 'admin'
    admin_password = 'admin'

    # Authenticate
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(main_url))
    admin_uid = common.authenticate(main_db, admin_username, admin_password, {})
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(main_url))

    # Signup a user
    # (would raise error, if user already exists)
    client_username = 'client-email@example.com'
    client_name = 'Client Name'
    client_password = 'Client Password'
    models.execute_kw(main_db, admin_uid, admin_password, 'res.users', 'signup', [{
        'login': client_username,
        'name': client_name,
        'password': client_password,
    }])

    # Authenticate the user at Main Database
    client_uid = common.authenticate(main_db, client_username, client_password, {})

    # Get user session at Main Database if needed
    params = {'db': main_db, 'login': client_username, 'password': client_password}
    data = json.dumps({'jsonrpc': '2.0', 'method': 'call', 'params': params})
    r = requests.post('%s/web/session/authenticate' % main_url,
                      data=data,
                      headers={'Content-Type':'application/json'})
    if not r.json()['result']['uid']:
        raise Exception('Authenticaion failed')
    client_session_id = r.json()['result']['session_id']


    # Create new Client database
    plan_id = 1  # specify plan you need
    client_db = 'client.odoo.local'

    # you can keep client_db empty to generate it automatically
    # from "DB Names" parameter in Plan's form

    client_db = False
    res = models.execute_kw(main_db, admin_uid, admin_password,
                            'saas_portal.plan', 'create_new_database',
                            [plan_id], {'dbname': client_db, 'user_id':client_uid})

    res['url']  # contains url for new database with client's access token.
    saas_portal_client_id = res['id']

    # Configure system
    data = {
        # configure addons
        'update_addons': [],
        'install_addons': ['sale', 'point_of_sale', 'stock', 'access_settings_menu', access_apps'],
        'uninstall_addons': [],
        # grant access to owner
        'access_owner_add': ['base.group_sale_manager', 'stock.group_stock_manager', 'access_settings_menu.group_show_settings_menu'],
        # restrict access for all users
        'access_remove': ['access_apps.group_show_modules_menu'],
        'params': [
             {'key': 'saas_client.max_users', 'value': 10, 'hidden': True}
        ],
    }
    res = models.execute_kw(main_db, admin_uid, admin_password,
                            'saas.config', 'do_upgrade_database',
                            [data, saas_portal_client_id])

Notes abouts API integration
----------------------------

* Be sure, that Portal module is installed at Main Database
* Be sure, that "Allow external users to sign up" option from "Settings/General Settings" is enabled (this option is only available in Debug mode)
* To find new signuped user open "Settings/Users" at Main Database and delete filter "Regular users only"
* don't use trailing slash at main_url
* Access token is expired in one hour
* In case of log out, client has to click "Log in via SaaS Portal". Client will be navigated to Portal database and can use client_username and client_password. After that the client will be returned back to his database. Important thing here, is that the client is not able to use client_password at login page of his database.
