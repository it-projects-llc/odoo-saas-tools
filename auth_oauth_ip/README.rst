=============================
 Local IP for OAuth requests
=============================

Allows to check access_token by requests in local network.

The module adds two fields to auth.oauth.provider:

* local_host
* local_port

This addresses is used on sending Authentication and Validation requests by using simple trick:

     # host - origin host for the URL
     # url - original host is replaced by local_host and local_port 
     urllib2.Request(url, headers={'host': host})

Credits
=======

Contributors
------------
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

HTML Description: https://apps.odoo.com/apps/modules/8.0/auth_oauth_ip/

Usage instructions: `<doc/index.rst>`__

Changelog: `<doc/changelog.rst>`__

Tested on Odoo 8.0 
