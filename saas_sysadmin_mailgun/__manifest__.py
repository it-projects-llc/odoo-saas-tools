# -*- coding: utf-8 -*-
{
    "name": """Saas Sysadmin Mailgun""",
    "summary": """This module configurates new databases for clients such as their users can send and receive mails""",
    "category": "SaaS",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "saas_sysadmin_aws_route53",
    ],
    "external_dependencies": {"python": ['boto'], "bin": []},
    "data": [
        "views/res_config.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
