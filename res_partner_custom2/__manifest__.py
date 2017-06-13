# -*- coding: utf-8 -*-
{
    "name": """res partner custom 2""",
    "summary": """custom fields in res.partner model""",
    "category": "base",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "base",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/res_partner_view.xml',
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
