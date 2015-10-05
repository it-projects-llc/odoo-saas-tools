{
    'name': 'SaaS Sysadmin Backup Agent S3',
    'version': '1.0.0',
    'author': 'Salton Massally<smassally@idtlabs.sl>',
    'category': 'SaaS',
    'website': 'http://idtlabs.sl',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': ['saas_sysadmin_backup_agent'],
    'data': [
        'views/res_config.xml',
        ],
    'installable': True,
}
