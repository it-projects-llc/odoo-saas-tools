:banner: banners/web_service_api.jpg
:force-toc: True

=================
 API integration
=================

To control SaaS via external tool `built-in XML-RPC <https://www.odoo.com/documentation/8.0/api_integration.html>`__ can be used.

Authenticate admin with SaaS Portal
===================================

All operations on SaaS Portal with client databases require authentication.

To authenticate admin with SaaS Portal:

::

   # Import libs
   import json
   import xmlrpclib
   import requests

   # Define credentials
   portal_url = <insert server URL>
   portal_db = <insert database name>
   admin_username = 'admin'
   admin_password = <insert password for your admin user (default: admin)>

   # Authenticate
   common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(portal_url))
   admin_uid = common.authenticate(portal_db, admin_username, admin_password, {})
   models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(portal_url))


Signup a user on SaaS Portal
============================


Before client database can be created a user of this client database should already exist on SaaS Portal.
There are several ways to create a new user in odoo.
Signup procedure creates users and assign the following groups to them:

* Portal
* View Online Payment Options

Membership in these groups gives users minimum privileges on SaaS Portal.


To signup a user:

::

   # Signup a user
   client_username = 'client-email@example.com'
   client_name = 'Client Name'
   client_password = 'Client Password'
   models.execute_kw(portal_db, admin_uid, admin_password, 'res.users', 'signup', [{
   'login': client_username,
   'name': client_name,
   'password': client_password,
   }])


Create client database
======================


To create client database:

::

   # Authenticate the user at Portal Database
   client_uid = common.authenticate(portal_db, client_username, client_password, {})
   # Create new Client database
   plan_id = 1  # specify plan you need
   client_db = 'client.odoo.local'
   # you can keep client_db empty to generate it automatically
   # from "DB Names" parameter in Plan's form
   owner_password = 'password of owner to log in his database'
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas_portal.plan', 'create_new_database',
                        [plan_id], {'dbname': client_db, 'user_id':client_uid, 'owner_password': owner_password})

There will be two users in just created client database:
 * admin
 * owner user

Groups assigned to owner in his database after creation:
 * Employee
 * Contact Creation


Get id of client database record on SaaS Portal
===============================================


Id of client database record on Portal should be known
to manipulate the client database from SaaS Portal

There are many ways to get the id.

* from plan_id and partner_id:
  ::

     # these values are given from other searches
     plan_id = 1
     partner_id = 7

     # search saas_portal.client on plan_id = 1 and partner_id = 7
     ids = models.execute_kw(portal_db, admin_uid, admin_password,
     'saas_portal.client', 'search',
     [[['plan_id', '=', plan_id], ['partner_id', '=', partner_id]]])

* from name of database (name of database is equal to domain host name):
  ::

     client_db = 'client.odoo.local'
     ids = models.execute_kw(portal_db, admin_uid, admin_password,
     'saas_portal.client', 'search',
     [[['name', '=', client_db]]])


Suspend client database
=======================


To suspend client database its id should be known.

To suspend:
::

   saas_portal_client_id = ids[0]
   data = {'params': [{'key': 'saas_client.suspended', 'value': '1', 'hidden': True}]}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])

To unsuspend/resume:
::

   saas_portal_client_id = ids[0]
   data = {'params': [{'key': 'saas_client.suspended', 'value': '0', 'hidden': True}]}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])



Limit number of users for client database
=========================================


Id of client database should be known.

To limit number of users for client database by 4:
::

   saas_portal_client_id = ids[0]
   data = {'params': [{'key': 'saas_client.max_users', 'value': '4', 'hidden': True}]}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])


Limit storage usage for client database
=======================================


Id of client database should be known.

To limit storage usage for client database by 500Mb:
::

   saas_portal_client_id = ids[0]
   data = {'params': [{'key': 'saas_client.total_storage_limit', 'value': '500', 'hidden': True}]}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])


Install/Uninstall modules in client database
============================================


Id of client database should be known.

To install the modules 'sale' and 'fleet' in client database:
::

   saas_portal_client_id = ids[0]
   data = {'install_addons': ['sale', 'fleet']}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])

To uninstall the module 'fleet' in client database:
::

   saas_portal_client_id = ids[0]
   data = {'uninstall_addons': ['fleet']}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])


Grant/restrict access rights for users in client database
=========================================================


To assign the sale manager and the stock manager groups to owner user:
::

   saas_portal_client_id = ids[0]
   data = {'access_owner_add': ['base.group_sale_manager', 'stock.group_stock_manager']}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])

To restrict access for all users by excluding them from the show modules menu group:
::

   saas_portal_client_id = ids[0]
   data = {'access_remove': ['access_apps.group_show_modules_menu']}
   res = models.execute_kw(portal_db, admin_uid, admin_password,
                        'saas.config', 'do_upgrade_database',
                        [data, saas_portal_client_id])

Notes abouts API integration
============================


* Be sure, that Portal module is installed at Main Database
* Be sure, that "Allow external users to sign up" option from "Settings/General Settings" is enabled (this option is only available in Debug mode)
* To find new signuped user open "Settings/Users" at Main Database and delete filter "Regular users only"
* don't use trailing slash at main_url
* Access token is expired in one hour
* In case of log out, client has to click "Log in via SaaS Portal". Client will be navigated to Portal database and can use client_username and client_password. After that the client will be returned back to his database. Important thing here, is that the client is not able to use client_password at login page of his database.
