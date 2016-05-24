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

plans = sock.execute_kw(db, uid, password, 'saas.api', 'get_all_plans', [json.dumps({'authenKey': '=5GPCkP^Q3lbw!x'})])
print plans