{
    'name': 'SaaS Portal Sale Subscription',
    'version': '11.0.1.0.0',
    'author': 'PlanetaTIC, IT-Projects LLC, Ildar Nasyrov, Nicolas JEUDY',
    'license': 'LGPL-3',
    'category': 'SaaS',
    'support': 'info@planetatic.com',
    'website': "https://www.planetatic.com",
    'depends': [
        'saas_portal_sale',
        'saas_portal_subscription',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/product_attribute_views.xml',
        'views/saas_portal.xml',
        'wizard/subscription_wizard.xml',
    ],
    'installable': True,
}
