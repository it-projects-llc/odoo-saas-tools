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
    'depends': ['saas_sysadmin'],
    'data': [
        'views/saas_sysadmin_route53.xml',
        'views/res_config.xml',
        ],
    'installable': True,
}
