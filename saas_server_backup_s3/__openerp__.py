# -*- coding: utf-8 -*-
{
    'name': 'SaaS Server Backup S3',
    'version': '1.0.0',
    'author': 'Salton Massally<smassally@idtlabs.sl>',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'http://idtlabs.sl',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': ['saas_server'],
    'data': [
        'views/res_config.xml',
    ],
    'installable': True,
}
