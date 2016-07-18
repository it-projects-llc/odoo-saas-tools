url = 'http://localhost:8069'
db = 'portal.saas.local'
username = 'admin'
password = '1'


import xmlrpclib
import json

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

uid = common.authenticate(db, username, password, {'authenKey': '=5GPCkP^Q3lbw!x'})

sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

# payload = {
#     # TODO: add configure mail server option here
#     'update_addons_list': 'base',
#     'update_addons': ['base'],
#     'install_addons': '',
#     'uninstall_addons': '',
#     'access_owner_add': '',
#     'access_remove': '',
#     'fixes': '',
#     'params': '',
#     'database': 'client-1.saas.local',
# }
#
# # upgrade base
# vals = sock.execute_kw(db, uid, password, 'saas.api', 'execute_instance', [json.dumps(payload)])
# print vals

#install sale
payload = {
    # TODO: add configure mail server option here
    'update_addons_list': [],
    'update_addons': [],
    'install_addons': ['sale'],
    'uninstall_addons': [],
    'access_owner_add': [],
    'access_remove': [],
    'fixes': [],
    'params': [],
    'database': 'client-1',
}
vals = sock.execute_kw(db, uid, password, 'saas.api', 'execute_instance', [json.dumps(payload)])
print vals
