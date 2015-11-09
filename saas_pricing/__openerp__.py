{
    'name': 'SaaS Pricing',
    'version': '1.0.0',
    'author': 'OpenJaf',
    'category': 'SaaS',
    'website': '',
    'depends': ['saas_server', 'saas_utils', 'saas_portal'],
    'data': [
        'views/saas_pricing.xml',
        'data.xml',
        ],
    'installable': True,

    'description': '''
        Module to define plans pricing
    ''',
}
