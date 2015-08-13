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
}
