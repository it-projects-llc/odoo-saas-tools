# -*- coding: utf-8 -*-
{
    'name': "Saas Portal Sale",
    'author': "IT-Projects LLC, Ildar Nasyrov",
    'license': 'LGPL-3',
    "support": "apps@it-projects.info",
    'website': "https://twitter.com/nasyrov_ildar",
    'category': 'SaaS',
    'version': '1.0.0',
    'depends': [
        'sale',
        'saas_portal',
        'product_price_factor',
        'saas_portal_start',
        'contract',
    ],
    'data': [
        'views/product_views.xml',
        'views/saas_portal.xml',
        'data/mail_template_data.xml',
        'data/ir_config_parameter.xml',
    ],
}
