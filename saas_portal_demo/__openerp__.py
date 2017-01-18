# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal Demo',
    'version': '0.1',
    'author': 'Cesar Lage',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'https://it-projects.info',
    'depends': ['saas_portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_portal.xml',
        'views/website.xml'
    ],
    'installable': True,
}
