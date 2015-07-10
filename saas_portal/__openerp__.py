{
    'name': 'SaaS Portal',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'category': 'SaaS',
    'website': 'https://it-projects.info',
    'depends': ['oauth_provider', 'website', 'auth_signup', 'saas_utils'],
    'data': [
        'views/wizard.xml',
        'views/saas_portal.xml',
        'views/res_config.xml',
        ],
    'installable': True,
}
