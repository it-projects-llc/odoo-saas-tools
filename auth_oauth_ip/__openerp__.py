# -*- coding: utf-8 -*-
{
    "name": """Local IP for OAuth requests""",
    "summary": """Allows to check access_token by requests in local network""",
    "category": "Extra Tools",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "auth_oauth",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views.xml",
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
