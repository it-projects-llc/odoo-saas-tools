# -*- coding: utf-8 -*-
{
    'name': 'SaaS System Administration Route 53',
    'summary': "Aws Route 53 integration for SAAS Tools",
    'version': '1.0.0',
    'author': 'Salton Massally <smassally@idtlabs.sl> (iDT Labs)',
    'license': 'LGPL-3',
    'category': 'SaaS',
    'website': 'idtlabs.sl',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': [
        'saas_sysadmin',
        'saas_sysadmin_aws',
        'saas_sysadmin_aws_route53',
    ],
    'data': [
    ],
    'installable': True,
}
