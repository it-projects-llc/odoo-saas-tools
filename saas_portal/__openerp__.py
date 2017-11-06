# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal',
    'version': '1.0.0',
    'author': 'Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'https://it-projects.info',
    'depends': ['oauth_provider', 'website', 'auth_signup', 'saas_base', 'saas_utils', 'base_automation'],
    'data': [
        'data/mail_template_data.xml',
        'data/plan_sequence.xml',
        'data/cron.xml',
        'wizard/config_wizard.xml',
        'wizard/batch_delete.xml',
        'wizard/subscription_wizard.xml',
        'views/saas_portal.xml',
        'views/res_config.xml',
        'data/ir_config_parameter.xml',
        'data/subtype.xml',
        'data/support_team.xml',
        'views/res_users.xml',
        'data/res_users.xml',
        'data/base_automation.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
