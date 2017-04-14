# -*- coding: utf-8 -*-
{
    "name": """Create databases after signup custom""",
    "summary": """Create several databases for new customers after signup""",
    "category": "SaaS",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        'saas_portal_sale',
        'saas_portal_signup',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/signup.xml',
        'views/saas_portal.xml',
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": False,
}
