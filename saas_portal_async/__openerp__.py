# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal Async database creation',
    'version': '1.0.0',
    'author': 'IT-Projects LLC',
    'website': "https://it-projects.info",
    'license': 'GPL-3',
    'category': 'SaaS',
    'depends': [
        'saas_portal',
        'connector',
    ],
    'installable': True,
    'application': False,
    'data': [
        'views/wizard.xml',
    ],
}
