# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal Asynchronous database creation',
    'version': '1.0.0',
    'author': 'IT-Projects LLC',
    'website': "https://it-projects.info",
    'license': 'GPL-3',
    'category': 'SaaS',
    'depends': [
        'base',
        'saas_portal',
        'saas_portal_sale',
        'connector',
    ],
    'installable': True,
    'application': False,
    'data': [
        'views/wizard.xml',
    ],
}
