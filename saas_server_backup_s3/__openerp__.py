# -*- coding: utf-8 -*-
{
    'name': 'SaaS Server Backup S3',
    'version': '1.0.0',
    'author': 'Salton Massally<smassally@idtlabs.sl>',
    'license': 'GPL-3',
    'category': 'SaaS',
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
