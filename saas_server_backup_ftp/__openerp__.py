# -*- coding: utf-8 -*-
{
    'name': "saas_server_backup_ftp",
    'author': "IT-Projects LLC, Ildar Nasyrov",
    'license': 'GPL-3',
    "support": "apps@it-projects.info",
    'website': "https://twitter.com/nasyrov_ildar",
    'category': 'SaaS',
    'version': '1.0.0',
    'depends': ['saas_server'],
    "external_dependencies": {"python": ['pysftp'], "bin": []},
    'data': [
        'views/res_config.xml',
        'data/ir_cron.xml',
    ],
}
