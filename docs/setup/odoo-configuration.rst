============================
 Configuration requirements
============================

Check official doc for understanding parameters: https://www.odoo.com/documentation/8.0/reference/cmdline.html

dbfilter
========

``dbfilter`` in config file or ``--db-filter`` parameter in running command must be::

    ^%h$
    
db_name
=======
be sure, that you don't use ``db_name`` in config file and don't run odoo with ``-d`` (``--database``) parameter

workers
=======

Set ``workers`` parameter to ``3`` or above. In some context it could be less, but ``3`` is enough at any case.

limit_time_cpu
==============

Increase this value. Set it 600 or more.

limit_time_real
==============

Increase this value. Set it 1200 or more.

addons_path
===========
It must include

* odoo addons
* odoo-saas-tools
* `dependencies <dependencies.rst>`__

db_user
=======

Installation script searches for database username in this parameter. In case it isn't set it uses ``odoo`` name as default.
Make sure that you have this parameter set in your configuration file or have ``odoo`` postgresql role.
