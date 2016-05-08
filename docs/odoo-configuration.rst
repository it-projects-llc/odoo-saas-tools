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
