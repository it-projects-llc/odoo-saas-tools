# -*- coding: utf-8 -*-
{
    "name": """Saas Server Demo""",
    "summary": """new parameters in __openerp__.py for demonstrative modules, control repositories for demonstration""",
    "category": "SaaS",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "saas_server",
    ],
    "external_dependencies": {"python": ['simplejson'], "bin": ['git']},
    "data": [
        "views/saas_server_demo.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
