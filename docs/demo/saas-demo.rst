=======================
How to deploy SaaS Demo
=======================

Shared Docker Network
=====================

::

 docker network create saas-demo-network

Configs
=======

::

 ODOO_MASTER_PASS=`< /dev/urandom tr -dc A-Za-z0-9 | head -c16;echo;`
 ODOO_DOMAIN="saas-demo.local"
 PORTAL_DB="${ODOO_DOMAIN}"

Nginx
=====

Nginx docker uses 8080 port on host. It means, that you need another (non-docker) nginx on your server.
If you don't need to have another nginx, replace 8080 to 80

::

 docker run \
 -p 8080:80 \
 --name odoo-nginx \
 --network=saas-demo-network \
 -t nginx

remove default config

::

 docker exec -i -t odoo-nginx rm /etc/nginx/conf.d/default.conf

upload nginx_odoo_params

::

  curl -s https://raw.githubusercontent.com/it-projects-llc/odoo-saas-tools/10.0/docs/demo/nginx_odoo_params > odoo_params
  docker cp odoo_params odoo-nginx:/etc/nginx/odoo_params


SaaS Portal
===========

db
--

::

 docker run --network=saas-demo-network -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo --name db-portal postgres:9.5

local repositories
------------------

::

 DOCKER_PARAMS=""

Local saas repo. Optional. Path before colons depends on your system.

::

 DOCKER_PARAMS="$DOCKER_PARAMS -v /mnt/files/odoo/odoo-8.0/odoo-saas-tools:/mnt/addons/it-projects-llc/odoo-saas-tools"



Portal odoo docker
------------------

::

 docker run \
 -e ODOO_MASTER_PASS=$ODOO_MASTER_PASS \
 -e DB_PORT_5432_TCP_ADDR=db-portal \
 $DOCKER_PARAMS \
 --name odoo-portal \
 --network=saas-demo-network \
 -t itprojectsllc/install-odoo:10.0 \
 -- \
 --db-filter=^%h$

press Ctrl-C

init saas
^^^^^^^^^

::

 INIT_SAAS_TOOLS_VALUE="\
 --portal-create \
 --odoo-script=/mnt/odoo-source/odoo-bin \
 --odoo-config=/mnt/config/odoo-server.conf \
 --admin-password=${ODOO_MASTER_PASS} \
 --portal-db-name=${PORTAL_DB} \
 --install-modules=saas_portal_demo \
 --odoo-without-demo \
 "

 docker exec -i -u root -t odoo-portal /bin/bash -c "export INIT_SAAS_TOOLS='$INIT_SAAS_TOOLS_VALUE'; bash /install-odoo-saas.sh"

nginx
^^^^^

::

 curl -s https://raw.githubusercontent.com/it-projects-llc/odoo-saas-tools/10.0/docs/demo/nginx_odoo.conf > portal.conf
 sed -i "s/NGINX_SERVER_DOMAIN/${ODOO_DOMAIN}/g" portal.conf
 sed -i "s/SERVER_HOST/odoo-portal/g" portal.conf
 docker cp portal.conf odoo-nginx:/etc/nginx/conf.d/portal.conf


SaaS Server
===========

* Select only one value

::

 SERVER_NAME="odoo-8" ODOO_BRANCH="8.0" ODOO_SCRIPT="/mnt/odoo-surce/openerp-server"
 SERVER_NAME="odoo-9" ODOO_BRANCH="9.0 "ODOO_SCRIPT="/mnt/odoo-surce/openerp-server"
 SERVER_NAME="odoo-10" ODOO_BRANCH="10.0" ODOO_SCRIPT="/mnt/odoo-surce/odoo-bin"

* Then execute commands below. After that repeat it with another odoo version.

db
--

::

 docker run --network=saas-demo-network -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo --name db-$SERVER_NAME postgres:9.5

Server odoo docker
------------------
Note. Don't forget to update the ``DOCKER_PARAMS`` variable if you used it to create a bind mount (like this ``-v /HOST_DIR:/CONTAINER_DIR``) - use appropriate branch for repo that you are binding

::

 docker run \
 --name $SERVER_NAME \
 -e DB_PORT_5432_TCP_ADDR=db-$SERVER_NAME \
 $DOCKER_PARAMS \
 --network=saas-demo-network \
 -t itprojectsllc/install-odoo:$ODOO_BRANCH \
 -- \
 --db-filter=^%d$

press Ctrl-C


Init saas
^^^^^^^^^

::

 INIT_SAAS_TOOLS_VALUE="\
 --server-create \
 --odoo-script=${ODOO_SCRIPT} \
 --odoo-config=/mnt/config/odoo-server.conf \
 --admin-password=${ODOO_MASTER_PASS} \
 --portal-db-name=${PORTAL_DB} \
 --server-db-name=${SERVER_NAME} \
 --server-hosts-template={dbname}.${SERVER_NAME}.{base_saas_domain} \
 --local-portal-host=odoo-portal \
 --local-server-host=${SERVER_NAME} \
 --install-modules=saas_server_demo,\
 saas_server_autodelete \
 --demo-repositories=\
 /mnt/addons/it-projects-llc/misc-addons,\
 /mnt/addons/it-projects-llc/pos-addons \
 --odoo-without-demo \
 "

 docker exec -u root -i -t $SERVER_NAME /bin/bash -c "export INIT_SAAS_TOOLS='$INIT_SAAS_TOOLS_VALUE'; bash /install-odoo-saas.sh"


call "create demo templates" on PORTAL

::

 INIT_SAAS_TOOLS_VALUE="\
 --odoo-script=/mnt/odoo-source/openerp-server \
 --odoo-config=/mnt/config/odoo-server.conf \
 --admin-password=${ODOO_MASTER_PASS} \
 --portal-db-name=${PORTAL_DB} \
 --server-db-name=${SERVER_NAME}.${ODOO_DOMAIN} \
 --create-demo-templates \
 "

 docker exec -u root -i -t odoo-portal /bin/bash -c "export INIT_SAAS_TOOLS='$INIT_SAAS_TOOLS_VALUE'; bash /install-odoo-saas.sh"


nginx proxing

::

 curl -s https://raw.githubusercontent.com/it-projects-llc/odoo-saas-tools/10.0/docs/demo/nginx_odoo.conf > nginx-${SERVER_NAME}.conf
 sed -i "s/NGINX_SERVER_DOMAIN/.${SERVER_NAME}.${ODOO_DOMAIN}/g" nginx-${SERVER_NAME}.conf
 sed -i "s/SERVER_HOST/${SERVER_NAME}/g" nginx-${SERVER_NAME}.conf
 docker cp nginx-${SERVER_NAME}.conf odoo-nginx:/etc/nginx/conf.d/${SERVER_NAME}.conf
 docker restart odoo-nginx
