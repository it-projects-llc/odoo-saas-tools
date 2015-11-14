{
    'name': 'SaaS System Admin Route 53 Healthcheck',
    'summary': "Aws Route 53 haelth check integration for SAAS Tools",
    'version': '1.0.0',
    'author': 'Salton Massally <smassally@idtlabs.sl>',
    'category': 'SaaS',
    'website': 'idtlabs.sl',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': ['saas_sysadmin_route53'],
    'data': [
        'views/saas_sysadmin_route53_healthcheck.xml',
        ],
    'installable': True,
}
