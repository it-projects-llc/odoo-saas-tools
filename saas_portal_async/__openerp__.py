# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal Asynchronous database creation',
    'version': '1.0.0',
    'author': 'IT-Projects LLC',
    "support": "apps@it-projects.info",
    'website': "https://it-projects.info",
    'license': 'GPL-3',
    'category': 'SaaS',
    'depends': [
        'base',
        'saas_portal',
        'connector',
    ],
    'installable': False,
    'application': False,
    'data': [
        'views/wizard.xml',
    ],
}
