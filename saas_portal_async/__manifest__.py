{
    'name': 'SaaS Portal Asynchronous database creation',
    'version': '11.0.1.0.0',
    'author': 'IT-Projects LLC, Nicolas JEUDY',
    "support": "apps@it-projects.info",
    'website': "https://it-projects.info",
    'license': 'GPL-3',
    'category': 'SaaS',
    'depends': [
        'base',
        'saas_portal',
        'connector',
    ],
    'installable': True,
    'application': False,
    'data': [
        'views/wizard.xml',
    ],
}
