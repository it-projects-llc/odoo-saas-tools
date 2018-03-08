{
    'name': 'SaaS Server Rotate Backup',
    'version': '11.0.1.0.0',
    'author': 'Salton Masssally, Nicolas JEUDY',
    'license': 'GPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'http://idtlabs.sl',
    'depends': ['saas_server'],
    'data': [
        'data/ir_cron.xml',
        'views/res_config.xml',
    ],
    'installable': True,
}
