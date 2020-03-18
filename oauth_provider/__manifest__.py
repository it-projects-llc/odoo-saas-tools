{
    'name': 'OAuth2 provider',
    'version': '11.0.1.0.0',
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
}
