# -*- coding: utf-8 -*-
{
    "name": """Demo datatabases""",
    "summary": """All you need to create demos for your applications in odoo apps store""",
    "category": "SaaS",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Cesar Lage, Ivan Yelizariev",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "saas_portal",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/saas_portal.xml",
        "views/website.xml"
    ],
    "qweb": [
    ],
    "demo": [
        "demo/saas_portal_plan.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
