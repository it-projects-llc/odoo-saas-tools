{
    'name': 'SaaS Server Rotate Backup S3',
    'version': '11.0.1.0.0',
    'author': 'Salton Masssally, Nicolas JEUDY',
    'license': 'GPL-3',
    'category': 'SaaS',
    "support": "apps@it-projects.info",
    'website': 'http://idtlabs.sl',
    'depends': ['saas_server', 'saas_server_backup_s3', 'saas_server_backup_rotate'],
    "external_dependencies": {"python": ['boto', 'rotate_backups_s3'], "bin": []},
    'data': [
    ],
    'installable': True,
}
