SaaS portal sale
================

With this module you can sale SaaS

Known issues
============

* base_action_rule 'on update' doesn't work with comuted fields in odoo 8.0.
  Therefore send_expiration_info() is not called on recomute expiration_datetime.
  Possible solution is to add cron task

Tested on Odoo 8.0 e84c01ebc1ef4fdf99865c45f10d7b6b4c4de229
