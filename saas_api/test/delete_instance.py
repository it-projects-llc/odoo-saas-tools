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

vals = sock.execute_kw(db, uid, password, 'saas.api', 'delete_instance', [json.dumps({'database_name': 'client-2'})])
print vals