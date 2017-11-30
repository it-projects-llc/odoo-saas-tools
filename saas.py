#!/usr/bin/env python
# -*- coding: utf-8 -*-

ODOO_VERSION = 10
SUPERUSER_ID = 1
SAAS_PORTAL_MODULES_REGEXP = '(saas_portal.*|saas_sysadmin.*)'
SAAS_SERVER_MODULES_REGEXP = '(saas_server.*)'

import ConfigParser
import argparse
import contextlib
import datetime
import fcntl
import re
import os
import psycopg2
import requests
import resource
import signal
import subprocess
import time
import traceback
import xmlrpclib


def log(*args):
    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print ''
    print ts
    print 'saas.py >>> ' + ', '.join([str(a) for a in args])

# ----------------------------------------------------------
# Options
# ----------------------------------------------------------

parser = argparse.ArgumentParser(description='''Control script to manage saas system.
It\'s assumed, that you have configured webserver (e.g. nginx). Check docs/port_80.rst for details.
''',
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 epilog='''
------------------------
Local usage:

   python saas.py
   sudo bash -c "python saas.py --print-local-hosts >> /etc/hosts"
''')

settings_group = parser.add_argument_group('Common settings')
settings_group.add_argument('--suffix', dest='suffix', default=ODOO_VERSION, help='suffix for names')
settings_group.add_argument('--odoo-script', dest='odoo_script', help='Path to odoo-server', default='./odoo-server')
settings_group.add_argument('--odoo-config', dest='odoo_config', help='Path to odoo configuration file')
settings_group.add_argument('--odoo-data-dir', dest='odoo_data_dir', help='Path to odoo data dir', default=None)
settings_group.add_argument('--odoo-xmlrpc-port', dest='xmlrpc_port', default='8069', help='Port to run odoo temporarly')
settings_group.add_argument('--odoo-longpolling-port', dest='longpolling_port', default='8072', help='Port to run odoo temporarly')
settings_group.add_argument('--use-existed-odoo', dest='use_existed_odoo', action='store_true', default=False, help='Wait infinitly for 8069 port. Usefull in docker environment.')
settings_group.add_argument('--local-xmlrpc-port', dest='local_xmlrpc_port', default=None, help='Port to be used for server-wide requests')
settings_group.add_argument('--local-portal-host', dest='local_portal_host', help='Address for internal connection to portal', default="localhost")
settings_group.add_argument('--local-server-host', dest='local_server_host', help='Address for internal connection to portal', default="localhost")
settings_group.add_argument('--odoo-log-db', dest='log_db', help='Logging database. The same as odoo parameter')
settings_group.add_argument("--odoo-addons-path", dest="addons_path",
                            help="specify additional addons paths (separated by commas).")
settings_group.add_argument('--odoo-db-filter', dest='db_filter', default='%h')
settings_group.add_argument('--odoo-test-enable', dest='test_enable', action='store_true')
settings_group.add_argument('--odoo-without-demo', dest='without_demo', action='store_true', default=False)
settings_group.add_argument('--master-password', dest='master_password', help='Master Password. Used on database creation.')
settings_group.add_argument('--admin-password', dest='admin_password', help='Password for admin user. It\'s used for all databases.', default='admin')
settings_group.add_argument('--base-domain', dest='base_domain', help='Base domain. Used for system that work with --db-filter=%d')
settings_group.add_argument('--dynamic-base-domain', dest='dynamic_base_domain', default=False, action='store_true', help='Force to keep Base domain empty. It will be updated on first admin logining')
settings_group.add_argument('--install-modules', dest='install_modules', help='Comma-separated list of modules to install. They will be automatically installed on appropriate database (Portal or Server)', default='saas_portal_start,saas_portal_sale_online')
#settings_group.add_argument('--db_user', dest='db_user', help='database user name')
settings_group.add_argument('-s', '--simulate', dest='simulate', action='store_true', help='Don\'t make actual changes. Just show what script is going to do.')
settings_group.add_argument('--drop-databases', dest='drop_databases', help='Drop existed databases before creating portal or server', action='store_true', default=False)


portal_group = parser.add_argument_group('Portal creation')
portal_group.add_argument('--portal-create', dest='portal_create', help='Create SaaS Portal database', action='store_true')
portal_group.add_argument('--portal-db-name', dest='portal_db_name', default='saas-portal-{suffix}.local')
portal_group.add_argument('--portal-modules', dest='portal_install_modules', help='Comma-separated list of modules to install on Portal', default='auth_signup')

server_group = parser.add_argument_group('Server creation')
server_group.add_argument('--server-create', dest='server_create', help='Create SaaS Server database', action='store_true')
server_group.add_argument('--server-db-name', dest='server_db_name', default='server-1.saas-portal-{suffix}.local')
server_group.add_argument('--server-modules', dest='server_install_modules', help='Comma-separated list of modules to install on Server')
server_group.add_argument('--server-hosts-template', dest='server_hosts_template',
                          help='server-wide host name template of client instances, i.e. {dbname}.odoo-10.{base_saas_domain}, {dbname} is the default')

plan_group = parser.add_argument_group('Plan creation')
plan_group.add_argument('--plan-create', dest='plan_create', help='Create Plan', action='store_true')
plan_group.add_argument('--plan-name', dest='plan_name', default='Plan')
plan_group.add_argument('--plan-template-db-name', dest='plan_template_db_name', default='template-1.saas-portal-{suffix}.local')
plan_group.add_argument('--plan-clients', dest='plan_clients', default='client-%i.saas-portal-{suffix}.local', help='Template for new client databases')

saas_demo = parser.add_argument_group('SaaS Demo')
saas_demo.add_argument('--demo-repositories', dest='demo_repositories',
                       help="Comma-separated list of path to repositories. "
                       "These repositories will be added to saas_server.repository table. "
                       "Note that path has to in addons-path.")
saas_demo.add_argument('--create-demo-templates', dest='create_demo_templates', action='store_true',
                       help="Create Plans and Templates to publish and demostrate modules")

other_group = parser.add_argument_group('Other')
other_group.add_argument('--print-local-hosts', dest='print_local_hosts', action='store_true', help='Print hosts rules for local usage.')
other_group.add_argument('--run', dest='run', action='store_true', help='Run server')
other_group.add_argument('--test', dest='test', action='store_true', help='Test system')
other_group.add_argument('--cleanup', dest='cleanup', action='store_true', help='Drop all saas databases. Use along with --simulate to check which database would be deleted')

args = vars(parser.parse_args())

# format vars
suffix = args['suffix']
for a in args:
    if isinstance(args[a], str) and not a == 'server_hosts_template':
        args[a] = args[a].format(suffix=suffix)


def get_odoo_config():
    res = {}
    config_file = args.get('odoo_config') or os.environ.get("OPENERP_SERVER")
    if not config_file:
        return res
    p = ConfigParser.ConfigParser()
    log('Read odoo config', config_file)
    p.read(config_file)
    for (name, value) in p.items('options'):
        if value == 'True' or value == 'true':
            value = True
        if value == 'False' or value == 'false':
            value = False
        res[name] = value
    return res

odoo_config = get_odoo_config()

datadir = args.get('odoo_data_dir') or odoo_config.get('data_dir')
xmlrpc_port = args.get('xmlrpc_port') or odoo_config.get('xmlrpc_port') or '8069'
local_xmlrpc_port = args.get('local_xmlrpc_port') or odoo_config.get('xmlrpc_port') or '8069'
longpolling_port = args.get('longpolling_port') or odoo_config.get('longpolling_port') or '8072'
master_password = args.get('master_password') or odoo_config.get('admin_passwd') or 'admin'

def filter_modules(s, regexp):
    return set([m for m in s.split(',') if re.match(regexp, m)])

portal_modules = filter_modules(args.get('install_modules', ''), SAAS_PORTAL_MODULES_REGEXP)
portal_modules.union((args.get('portal_install_modules') or '').split(','))
portal_modules.add('saas_portal')

server_modules = filter_modules(args.get('install_modules', ''), SAAS_SERVER_MODULES_REGEXP)
server_modules.union((args.get('server_install_modules') or '').split(','))
server_modules.add('saas_server')

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------


def main():
    if args.get('print_local_hosts'):
        host_line = '127.0.0.1 %s'
        print ''
        print '# generated by odoo-saas-tools'
        for host in ['portal_db_name', 'server_db_name', 'plan_template_db_name']:
            print host_line % args.get(host)
        for i in range(1, 11):
            print host_line % (args.get('plan_clients').replace('%i', '%03i' % i))
        return

    if args.get('simulate'):
        log('SIMULATION MODE')

    if args.get('cleanup'):
        cleanup()

    # run odoo to make updates via rpc
    error = None
    plan_id = None
    pid = None

    port_is_open = wait_net_service('127.0.0.1', int(xmlrpc_port), 3 if not args.get('use_existed_odoo') else False)
    if port_is_open:
        log('Port is used. Probably, odoo is already running. Let\'s try to use it. It it will fail, you need either stop odoo or pass another port to saas.py via --xmlrpc-port arg')
    else:
        cmd = get_cmd()
        pid = spawn_cmd(cmd)
    try:
        port_is_open or wait_net_service('127.0.0.1', int(xmlrpc_port), 30)

        if args.get('portal_create'):
            createdb(args.get('portal_db_name'))
            rpc_init_db(args.get('portal_db_name'),
                        install_modules=portal_modules)
            rpc_init_portal(args.get('portal_db_name'))

        if args.get('server_create'):
            createdb(args.get('server_db_name'))
            rpc_init_db(args.get('server_db_name'),
                        install_modules=server_modules)
            rpc_init_server(args.get('server_db_name'))
            rpc_add_server_to_portal(args.get('portal_db_name'))

        if args.get('plan_create'):
            plan_id = rpc_create_plan(args.get('portal_db_name'))

        if args.get('demo_repositories'):
            rpc_add_demo_repositories(args.get('demo_repositories'))

        if args.get('create_demo_templates'):
            rpc_create_demo_templates()

        if args.get('test'):
            if not plan_id:
                # TODO get plan_id
                plan_id = 1
            rpc_run_tests(args.get('portal_db_name'), plan_id)
            log('SaaS tests were passed successfully')

    except Exception as e:
        error = e
        traceback.print_exc()
    if pid:
        kill(pid)

    if error:
        return

    if args.get('run'):
        if args.get('portal_create'):
            print '\n\n\n\n\n     ------ ====== THE SAAS SYSTEM IS READY ===== -----     \n\n\n\n\n'

        cmd = get_cmd(run_cron=True)
        exec_cmd(cmd)


# ----------------------------------------------------------
# Tools
# ----------------------------------------------------------
def createdb(dbname):
    if args.get('drop_databases'):
        pg_dropdb(dbname)
    without_demo = args.get('without_demo')
    main_url = 'http://localhost:%s' % xmlrpc_port
    demo = not without_demo
    lang = 'en_US'  # TODO
    admin_password = args.get('admin_password')

    rpc_db = xmlrpclib.ServerProxy('{}/xmlrpc/2/db'.format(main_url))

    # create db if not exist
    created = False
    log('create database via xmlrpc', dbname)
    try:
        rpc_db.create_database(master_password, dbname, demo, lang, admin_password)
        created = True
    except Exception, e:
        log('xmlrpc database creation error:', e)

    return created

def dropdb(dbname):
    pg_dropdb(dbname)
    # cleanup filestore
    # paths = [os.path.join(datadir, pn, 'filestore', dbname) for pn in 'OpenERP Odoo'.split()]
    paths = [os.path.join(datadir, 'filestore', dbname)]
    exec_cmd(['rm', '-rf'] + paths)


def cleanup():
    for dbname in find_databases(args.get('portal_db_name')):
        dropdb(dbname)


# ----------------------------------------------------------
# RPC Tools
# ----------------------------------------------------------
def rpc_auth(dbname, admin_username='admin', admin_password='admin', host='localhost'):
    main_url = 'http://%s:%s' % (host, xmlrpc_port)
    if args.get('simulate'):
        return None, None, None, None

    # Authenticate
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(main_url))
    admin_uid = common.authenticate(dbname, admin_username, admin_password, {})
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(main_url))
    assert admin_uid, 'Authentication failed %s' % ((dbname, admin_username, admin_password),)

    return dbname, models, admin_uid, admin_password


def rpc_execute_kw(auth, model, method, rpc_args=[], rpc_kwargs={}):
    dbname, models, admin_uid, admin_password = auth
    log('auth', auth)
    log('RPC Execute', model, method, rpc_args, rpc_kwargs)
    if args.get('simulate'):
        return
    return models.execute_kw(dbname, admin_uid, admin_password,
                             model, method, rpc_args, rpc_kwargs)

def rpc_init_db(dbname, install_modules=None, new_admin_password=None):
    auth = rpc_auth(dbname, admin_password=args.get('admin_password'))
    if install_modules:
        test_enable = args.get('test_enable')
        domain = [('state', '=', 'uninstalled'), ('name', 'in', list(install_modules))]
        module_ids = rpc_execute_kw(auth, 'ir.module.module', 'search', [domain])
        rpc_execute_kw(auth, 'ir.module.module', 'button_immediate_install', [module_ids])

    if new_admin_password:
        rpc_execute_kw(auth, 'res.users', 'write', [[SUPERUSER_ID], {
            'password': new_admin_password,
        }])


def rpc_init_portal(dbname):
    # * open Settings/Configuration/SaaS Portal Settings
    #   * set *Base SaaS domain*, e.g. **odoo.local**
    #   * click Apply (do it even if you didn't make changes)
    auth = rpc_auth(dbname, admin_password=args.get('admin_password'))
    base_saas_domain = dbname
    if args.get('base_domain') and '.' not in dbname:
        base_saas_domain = args.get('base_domain')
    if not args.get('dynamic_base_domain'):
        rpc_execute_kw(auth, 'ir.config_parameter', 'set_param', ['saas_portal.base_saas_domain', base_saas_domain])

    # Allow external users to sign up
    rpc_execute_kw(auth, 'ir.config_parameter', 'set_param', ['auth_signup.allow_uninvited', repr(True)])


def rpc_init_server(server_db_name):
    # Update OAuth Provider urls
    auth = rpc_auth(server_db_name, admin_password=args.get('admin_password'))
    portal_host = args.get('portal_db_name')
    if args.get('base_domain') and '.' not in portal_host:
        portal_host = '%s.%s' % (portal_host, args.get('base_domain'))
    oauth_provider = rpc_xmlid_to_object(auth, 'saas_server.saas_oauth_provider', 'auth.oauth.provider')
    vals = {
        'auth_endpoint': oauth_provider.get('auth_endpoint').replace('odoo.local', portal_host),
        'validation_endpoint': oauth_provider.get('validation_endpoint').replace('odoo.local', portal_host),
        'local_host': args.get('local_portal_host'),
        'local_port': local_xmlrpc_port,
    }
    oauth_provider = rpc_execute_kw(auth, 'auth.oauth.provider', 'write', [[oauth_provider.get('id')], vals])


def rpc_add_server_to_portal(portal_db_name):
    # 5. Register Server Database in Main Database
    #    * open SaaS/SaaS/Servers
    #      * click [Create]
    #      * set Database Name, e.g. **s1.odoo.local**
    #      * fix autogenerated Database UUID to actual one (see previous section)
    #      * click [Save]
    auth = rpc_auth(portal_db_name, admin_password=args.get('admin_password'), host=args.get('local_portal_host'))
    server_db_name = args.get('server_db_name')
    uuid = rpc_get_uuid(server_db_name)
    vals = {
            'name': server_db_name,
            'client_id': uuid,
            'local_port': local_xmlrpc_port,
            'local_host': args.get('local_server_host'),
            'password': args.get('admin_password'),
    }
    server_hosts_template = args.get('server_hosts_template')
    if server_hosts_template:
        vals.update({'clients_host_template': server_hosts_template})
    rpc_execute_kw(auth, 'saas_portal.server', 'create', [vals])


def rpc_add_demo_repositories(demo_repositories):
    demo_repositories = demo_repositories.split(',')
    server_db_name = args.get('server_db_name')
    auth = rpc_auth(server_db_name, admin_password=args.get('admin_password'))
    for repo_path in demo_repositories:
        vals = {
            'path': repo_path,
        }
        rpc_execute_kw(auth, 'saas_server.repository', 'create', [vals])


def rpc_create_demo_templates():
    # auth to portal
    portal_db_name = args.get('portal_db_name')
    auth = rpc_auth(portal_db_name, admin_password=args.get('admin_password'))

    # find server
    server_db_name = args.get('server_db_name')
    server_id = rpc_get_server_id(auth, server_db_name)

    # execute
    rpc_execute_kw(auth, 'saas_portal.server', 'update_repositories', [[server_id]])
    rpc_execute_kw(auth, 'saas_portal.server', 'generate_demo_plans', [[server_id]])
    rpc_execute_kw(auth, 'saas_portal.server', 'create_demo_templates', [[server_id]])


def rpc_get_uuid(dbname):
    auth = rpc_auth(dbname, admin_password=args.get('admin_password'))
    res = rpc_execute_kw(auth, 'ir.config_parameter', 'get_param', ['database.uuid'])
    return res


def rpc_xmlid_to_object(auth, xmlid, model):
    res_id = rpc_execute_kw(auth, 'ir.model.data', 'xmlid_to_res_id', [xmlid])
    read = rpc_execute_kw(auth, model, 'read', [res_id])
    if read:
        return read[0]
    else:
        return None


def rpc_get_server_id(auth, server_db_name):
    res = rpc_execute_kw(auth, 'saas_portal.server', 'search', [[('name', '=', server_db_name)]])
    server_id = res[0]
    return server_id


def rpc_create_plan(portal_db_name):
    plan_name = args.get('plan_name')
    plan_template_db_name = args.get('plan_template_db_name')
    plan_clients = args.get('plan_clients')

    auth = rpc_auth(portal_db_name, admin_password=args.get('admin_password'))

    # 6. Create Plan
    #    * open Saas/SaaS/Plans
    #      * click [Create]
    #      * set Plan's name, e.g. "POS + ECommerce"
    #      * set SaaS Server
    #      * set Template DB: type name, e.g. **t1.odoo.local**, and click *Create "__t1.odoo.local__"*
    #      * click [Save]

    # TODO: use rpc_get_server_id
    res = rpc_execute_kw(auth, 'saas_portal.server', 'search', [[]])
    # use last created server
    log('search server', res)
    server_id = res[0]

    template_id = rpc_execute_kw(auth, 'saas_portal.database', 'create', [{'name': plan_template_db_name}])

    plan_id = rpc_execute_kw(auth, 'saas_portal.plan', 'create', [{'name': plan_name, 'server_id': server_id, 'template_id': template_id, 'dbname_template': plan_clients}])

    #      * click [Create Template DB].
    #      * wait couple minutes while Database is being created.
    dropdb(plan_template_db_name)
    rpc_execute_kw(auth, 'saas_portal.plan', 'create_template', [[plan_id]])

    return plan_id


def rpc_run_tests(portal_db_name, plan_id):
    auth = rpc_auth(portal_db_name, admin_password=args.get('admin_password'))
    create_new_database = rpc_execute_kw(auth, 'saas_portal.plan', 'create_new_database', [[plan_id]])
    rpc_execute_kw(auth, 'saas_portal.plan', 'action_sync_server', [[plan_id]])
    # works only in configured environment, i.e. dns and nginx are configured.
    # On runbot the condistions are not satisfied
    # so just comment it out
    # requests.get(create_new_database.get('auth_url'))

# some functions below were taken from runbot module: https://github.com/odoo/odoo-extra/tree/master/runbot
# ----------------------------------------------------------
# DB Tools
# ----------------------------------------------------------


def pg_createdb(dbname, without_demo=True):
    log('Creating empty database %s' % dbname)
    if args.get('simulate'):
        return
    with pgadmin_cursor() as local_cr:
        local_cr.execute("""CREATE DATABASE "%s" TEMPLATE template0 LC_COLLATE 'C' ENCODING 'unicode'""" % dbname)
        log('Result: %s' % local_cr.statusmessage)


def pg_dropdb(dbname):
    log('Dropping  database %s' % dbname)
    if args.get('simulate'):
        return
    with pgadmin_cursor() as local_cr:
        local_cr.execute('DROP DATABASE IF EXISTS "%s"' % dbname)
        log('Result: %s' % local_cr.statusmessage)


def find_databases(root_database):
    with pgadmin_cursor() as local_cr:
        local_cr.execute("SELECT datname FROM pg_database WHERE  datname ilike '%%.{root}' OR datname='{root}'".format(root=root_database))
        res = local_cr.fetchall()
    return [row[0] for row in res]


def exec_pg_environ():
    """
    Force the database PostgreSQL environment variables to the database
    configuration of Odoo.

    Note: On systems where pg_restore/pg_dump require an explicit password
    (i.e.  on Windows where TCP sockets are used), it is necessary to pass the
    postgres user password in the PGPASSWORD environment variable or in a
    special .pgpass file.

    See also http://www.postgresql.org/docs/8.4/static/libpq-envars.html
    """
    env = os.environ.copy()
    db_user = odoo_config.get('db_user') or os.getenv('DB_ENV_POSTGRES_USER') or os.getenv('RDS_USERNAME') or os.getenv('PGUSER') or 'odoo'
    if db_user:
        env['PGUSER'] = db_user
    db_host = odoo_config.get('db_host') or os.getenv('DB_PORT_5432_TCP_ADDR') or os.getenv('RDS_HOSTNAME')
    if db_host:
        env['PGHOST'] = db_host
    db_port = odoo_config.get('db_port') or os.getenv('DB_PORT_5432_TCP_PORT') or os.getenv('RDS_PORT') or os.getenv('PGPORT') or '5432'
    if db_port:
        env['PGPORT'] = db_port

    db_password = odoo_config.get('db_password') or os.getenv('DB_ENV_POSTGRES_PASSWORD') or os.getenv('RDS_PASSWORD') or os.getenv('PGPASSWORD') or 'odoo'
    if db_password:
        env['PGPASSWORD'] = db_password

    return env


@contextlib.contextmanager
def pgadmin_cursor():
    env = exec_pg_environ()
    cnx = None
    try:
        cnx = psycopg2.connect(database="postgres",
                               user=env.get('PGUSER'),
                               password=env.get('PGPASSWORD'),
                               host=env.get('PGHOST'),
                               port=env.get('PGPORT'),
                               )
        cnx.autocommit = True  # required for admin commands
        yield cnx.cursor()
    finally:
        if cnx:
            cnx.close()


# ----------------------------------------------------------
# OS Tools
# ----------------------------------------------------------
def get_cmd(dbname='', workers=3, run_cron=False):
    cmd = [
        args.get('odoo_script'),
        "--xmlrpc-port=%s" % xmlrpc_port,
        "--longpolling-port=%s" % longpolling_port,
        "--database=%s" % dbname,
        "--db-filter=%s" % args.get('db_filter'),
        "--workers=%s" % workers,
    ]
    env = exec_pg_environ()
    for env_key, config_key in \
        [('PGUSER', '--db_user'),
         ('PGPASSWORD', '--db_password'),
         ('PGHOST', '--db_host'),
         ('PGPORT', '--db_port'),
         ]:
        if env.get(env_key):
            cmd += [config_key + '=' + env.get(env_key)]

    if not run_cron:
        cmd += ["--max-cron-threads=0"]

    if args.get('odoo_config'):
        cmd += ['--config=%s' % args.get('odoo_config')]

    if args.get('log_db'):
        cmd += ['--log-db=%s' % args.get('log_db')]

    if args.get('addons_path'):
        cmd += ['--addons-path=%s' % args.get('addons_path')]

    if os.getenv('SAAS_ODOO_PARAMS'):
        cmd += os.getenv('SAAS_ODOO_PARAMS').split(' ')

    return cmd


def exec_cmd(cmd):
    log('EXEC: ', ' '.join(cmd))
    if args.get('simulate'):
        return
    os.system(' '.join(cmd))


def spawn_cmd(cmd, cpu_limit=None, shell=False):
    log('Spawn', ' '.join(cmd))
    if args.get('simulate'):
        return

    def preexec_fn():
        os.setsid()
        if cpu_limit:
            # set soft cpulimit
            soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
            r = resource.getrusage(resource.RUSAGE_SELF)
            cpu_time = r.ru_utime + r.ru_stime
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_time + cpu_limit, hard))
        # close parent files
        os.closerange(3, os.sysconf("SC_OPEN_MAX"))
        # lock(lock_path)
    # out=open(log_path,"w")
    # _logger.debug("spawn: %s stdout: %s", ' '.join(cmd), log_path)
    p = subprocess.Popen(cmd,
                         # stdout=out,
                         # stderr=out,
                         preexec_fn=preexec_fn,
                         shell=shell)
    log('Spawn pid: %s' % p.pid)
    return p.pid


def kill(pid):
    log('KILL', pid)
    if args.get('simulate'):
        return
    try:
        os.killpg(pid, signal.SIGKILL)
    except OSError:
        pass


# http://code.activestate.com/recipes/576655-wait-for-network-service-to-appear/
def wait_net_service(server, port, timeout=None):
    """ Wait for network service to appear
        @param timeout: in seconds, if None or 0 wait forever
        @return: True of False, if timeout is None may return only True or
                 throw unhandled network exception
    """
    log('Waiting for port', server, port)

    if args.get('simulate'):
        return

    import socket

    s = socket.socket()
    if timeout:
        from time import time as now
        # time module is needed to calc timeout shared between two exceptions
        end = now() + timeout

    while True:
        try:
            if timeout:
                next_timeout = end - now()
                if next_timeout < 0:
                    return False
                else:
                    s.settimeout(next_timeout)

            s.connect((server, port))

        except socket.timeout as err:
            # this exception occurs only if timeout is set
            if timeout:
                log('Port timeout')
                return False

        except socket.error as err:
            pass
        else:
            s.close()
            return True


if __name__ == "__main__":
    main()
