{
    'name': 'SaaS Server',
    'version': '11.0.1.0.0',
    'author': 'Ivan Yelizariev, Nicolas JEUDY',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'https://it-projects.info',
    'depends': [
        'auth_oauth',
        'auth_oauth_ip',
        'saas_base',
        'website',
    ],
    'data': [
        'views/saas_server.xml',
        'views/res_config_settings_views.xml',
        'data/auth_oauth_data.xml',
        'data/ir_config_parameter.xml',
        'data/pre_install.yml',
    ],
    'installable': True,
}
