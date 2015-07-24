{
    'name': 'SaaS Client',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'SaaS',
    'website': 'https://it-projects.info',
    'depends': ['auth_oauth', 'auth_oauth_check_client_id', 'saas_utils', 'mail'],
    'data': [
        'views/saas_client.xml',
        'security/rules.xml',
        'data/ir_cron.xml',
        'data/auth_oauth_data.xml',
    ],
    'installable': True,
    'description': '''

Module for client database. You have to install this module
on template database (see saas_portal module)

INSTALLATION
============

Server wide
-----------

You have to mark as server wide:

* this module
* module auth_oauth
    ''',
}
