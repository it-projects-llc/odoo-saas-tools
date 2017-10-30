# -*- coding: utf-8 -*-
{
    "name": """Account custom2 security""",
    "summary": """Make Settings menu in Accounting available to group_erp_manager (Access Rights)""",
    "category": "Accounting",
    # "live_test_url": "",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/iledarn",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "sale",
        'access_restricted',
        'access_apps',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/custom2_security.xml',
        'views/base_menu.xml',
        'security/ir.model.access.csv',
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
