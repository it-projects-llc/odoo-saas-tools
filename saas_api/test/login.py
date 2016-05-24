url = 'http://localhost:8069'
db = 'portal.saas.local'
username = 'admin'
password = '1'


import xmlrpclib

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

uid = common.authenticate(db, username, password, {'authenKey': '=5GPCkP^Q3lbw!x'})

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
