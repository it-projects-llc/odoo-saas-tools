{
    'name': 'SaaS Server - Autodelete expired databases',
    'version': '11.0.1.0.0',
    'author': 'Ivan Yelizariev, Nicolas JEUDY',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'https://it-projects.info',
    'depends': ['saas_server'],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
}
