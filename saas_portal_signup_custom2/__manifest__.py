# -*- coding: utf-8 -*-
{
    'name': "saas_portal_signup_custom2",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'auth_signup',
                'saas_portal',
                'saas_portal_sale',
                'saas_portal_portal',
                'website_sale',
                'res_partner_custom2',
                'theme_kit',
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/auth_signup_login_templates.xml',
        'views/website_templates.xml',
        'views/website_portal_sale_templates.xml',
        'views/res_config_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
