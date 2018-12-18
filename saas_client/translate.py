# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC <info@planetatic.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_sparse_field.models.fields import monkey_patch
from odoo.tools.translate import GettextAlias


@monkey_patch(GettextAlias)
def _get_cr(self, frame, allow_create=True):
    # try, in order: cr, cursor, self.env.cr, self.cr,
    # request.env.cr
    if 'cr' in frame.f_locals:
        return frame.f_locals['cr'], False
    if 'cursor' in frame.f_locals:
        return frame.f_locals['cursor'], False
    s = frame.f_locals.get('self')
    if hasattr(s, 'env'):
        return s.env.cr, False
    if hasattr(s, 'cr'):
        return s.cr, False
    # Don't get cursor from request as its database can be different from the
    # one in the thread!
#     try:
#         from odoo.http import request
#         return request.env.cr, False
#     except RuntimeError:
#         pass
    if allow_create:
        # create a new cursor
        db = self._get_db()
        if db is not None:
            return db.cursor(), True
    return None, False
