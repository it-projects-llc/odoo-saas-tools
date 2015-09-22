{
    'name': 'SaaS Server',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'SaaS',
    'website': 'https://it-projects.info',
    'depends': ['auth_oauth', 'saas_base', 'saas_utils', 'website'],
    'data': [
        'views/saas_server.xml',
        'views/res_config.xml',
        'data/auth_oauth_data.xml',
        'data/ir_config_parameter.xml',
        'data/pre_install.yml',
    ],
    'installable': True,
}
