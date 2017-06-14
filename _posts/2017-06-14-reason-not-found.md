---
layout:     post
title:      "Typical installation problem: 404 NOT FOUND"
subtitle:   "Got Error on request /saas_server/new_database ?"
date:       2017-06-14 00:00:00
author:     "Ivan Yelizariev"
header-img: "img/posts/matrix.jpg"
comments: true
tags: [ FAQ ]
---

# Error
One of typical installation problem looks as following:

```
2016-07-17 20:50:48,590 21379 INFO None werkzeug: 127.0.0.1 - - [17/Jul/2016 20:50:48] "GET /saas_server/new_database HTTP/1.0" 404 -
2016-07-17 20:50:48,591 21381 ERROR odoo.local openerp.http: Exception during JSON request handling.
Traceback (most recent call last):
  File "/opt/odoo/openerp/http.py", line 543, in _handle_exception
    return super(JsonRequest, self)._handle_exception(exception)
  File "/opt/odoo/openerp/http.py", line 580, in dispatch
    result = self._call_function(**self.params)
  File "/opt/odoo/openerp/http.py", line 316, in _call_function
    return checked_call(self.db, *args, **kwargs)
  File "/opt/odoo/openerp/service/model.py", line 118, in wrapper
    return f(dbname, *args, **kwargs)
  File "/opt/odoo/openerp/http.py", line 313, in checked_call
    return self.endpoint(*a, **kw)
  File "/opt/odoo/openerp/http.py", line 809, in __call__
    return self.method(*args, **kw)
  File "/opt/odoo/openerp/http.py", line 409, in response_wrap
    response = f(*args, **kw)
  File "/opt/odoo/openerp/addons/web/controllers/main.py", line 948, in call_button
    action = self._call_kw(model, method, args, {})
  File "/opt/odoo/openerp/addons/web/controllers/main.py", line 936, in _call_kw
    return getattr(request.registry.get(model), method)(request.cr, request.uid, *args, **kwargs)
  File "/opt/odoo/openerp/api.py", line 268, in wrapper
    return old_api(self, *args, **kwargs)
  File "/opt/odoo/openerp/api.py", line 399, in old_api
    result = method(recs, *args, **kwargs)
  File "/opt/odoo/odoo-saas-tools/saas_portal/models/saas_portal.py", line 367, in create_template
    raise Warning('Error on request: %s\nReason: %s \n Message: %s' % (req.url, res.reason, res.content))
Warning: Error on request: http://s1.odoo.local:80/saas_server/new_database
Reason: NOT FOUND 
 Message: <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server.</p><p>If you entered the URL manually please check your spelling and try again.</p>
```

The error is raised when you try to create new *SaaS Client*.

# Solution

The reason of this problem in wrong [db-filter](https://www.odoo.com/documentation/10.0/setup/deploy.html#dbfilter) value. It has to be either ``^%h$`` or ``^%d$`` (depends on type of database names you use). There are two ways to specify the parameter:

Either update config file:
```
dbfilter = ^%h$
```
or add parameter on start command:
```
./odoo-bin --config=/etc/openerp-server.conf --db-filter=^%h$
```

# Explanation

The page ``/saas_server/new_database`` actually exists, but odoo return 404 because it doesn't know on which database it has to get it. The parameter ``db-filter`` allows to specify which database to use depending on host name of a request.
