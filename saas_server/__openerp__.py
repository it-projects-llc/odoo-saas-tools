{
    'name': 'SaaS Server',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'SaaS',
    'website': 'https://it-projects.info',
    'depends': ['auth_oauth', 'saas_base', 'saas_utils', 'website'],
    'data': [
        'views/saas_server.xml',
        'data/auth_oauth_data.xml',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/pre_install.yml',
    ],
    'installable': True,
    'description': '''

Module for central database on odoo databases cluster. Cluster is a odoo
installation. Each cluster is located on a separate server, in the main.

Functions
---------

* create new databases
* copy oauth provider data to new database
* collect information about databases

Usage
=====

* You have to use --db-filter option  so that database with this module be determine unambiguously by host of request
* install this module
* Configure oauth provider data

    ''',
}
