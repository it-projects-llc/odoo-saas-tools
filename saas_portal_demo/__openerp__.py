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
        "saas_portal_sale_online",
        "website_seo_url",
        "website_seo_url_product",
        "website_sale_add_to_cart_disable",
    ],
    "external_dependencies": {"python": ['requests'], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        # "views/saas_portal.xml",
        # "views/website.xml"
        "views/templates.xml",
        "views/saas_portal_demo.xml",
        "views/product.xml",
        "data/product.xml",
        "data/ir_cron.xml",
    ],
    "qweb": [
    ],
    "demo": [
        # "demo/saas_portal_plan.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
