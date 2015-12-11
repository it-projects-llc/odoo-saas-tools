SaaS portal sale
================

With this module you can sale SaaS

Known issues
============

* base_action_rule 'on update' doesn't work with comuted fields in odoo 8.0.
  Therefore send_expiration_info() is not called on recomute expiration_datetime.
  Possible solution is to add cron task

Tested on Odoo 9.0 901a3e030c4b11a219abf391839a471025bab4b3
