{
    'name' : 'SaaS Server',
    'version' : '1.0.0',
    'author' : 'Ivan Yelizariev',
    'category' : 'SaaS',
    'website' : 'https://it-projects.info',

    'depends' : ['auth_oauth'],
    'data':[
        'data/auth_oauth_data.xml'
        ],
    'installable': True,

    'description': '''
Module for central database on odoo databases cluster. Cluster is a odoo installation. Each cluster is located on a separate server, in the main.

Functions:

* create new databases
* collect information about databases
    ''',
}
