{
    'name': 'SaaS Pricing',
    'version': '1.0.0',
    'author': 'OpenJaf',
    'license': 'LGPL-3',
    'category': 'SaaS',
    'website': '',
    'depends': ['saas_server', 'saas_utils', 'saas_portal'],
    'data': [
        'views/saas_pricing.xml',
        ],
    'installable': False,

    'description': '''
        Module to define plans pricing
    ''',
}
