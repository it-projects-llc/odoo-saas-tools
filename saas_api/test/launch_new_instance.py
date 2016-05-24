url = 'http://localhost:8069'
db = 'portal.saas.local'
username = 'admin'
password = '1'

import json
import xmlrpclib

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

uid = common.authenticate(db, username, password, {'authenKey': '=5GPCkP^Q3lbw!x'})

sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')

user  = {
    'name': 'Nguyen Van A',
    'login': 'vana',
    'email': 'thanhchatvn@gmail.com',
    'password': '123456789',
    'mobile': '0902403918',
    'fe_id': 12,
}
plan = {
    'plan_id': 1
}
database = {
    'name': 'launch1',
}

datas = json.dumps({'user': user, 'plan': plan, 'database': database})
new_instance = sock.execute_kw(db, uid, password, 'saas.api', 'launch_new_instance', [datas])
print new_instance
