{
    'name': 'SaaS System Administration Route 53',
    'summary': "Aws Route 53 integration for SAAS Tools",
    'description': """
        Integrates AWS Route53 with SAAS Portal providing enabling the 
        creation on DNS recordset when servers or database are added
    """,
    'version': '1.0.0',
    'author': 'Salton Massally <smassally@idtlabs.sl> (iDT Labs)',
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
