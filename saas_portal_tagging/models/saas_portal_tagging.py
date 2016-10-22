# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning


class SaasPortalCategory(models.Model):

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.display_name))
        return res

    @api.one
    @api.depends('name')
    def _name_get_fnc(self):
        name = self.name
        if self.parent_id:
            name = self.parent_id.name + ' / ' + name
        self.display_name = name

    _name = "saas.portal.category"
    _description = "SaaS Client  Category"
    name = fields.Char(
        "Employee Tag",
        required=True
    )
    display_name = fields.Char(
        'Name',
        compute='_name_get_fnc',
        store=True,
        readonly=True
    )
    parent_id = fields.Many2one(
        'saas.portal.category',
        'Parent Employee Tag',
        index=True
    )
    child_ids = fields.One2many(
        'saas.portal.category',
        'parent_id',
        'Child Categories'
    )

    @api.constrains('parent_id')
    @api.multi
    def _check_recursion(self):
        level = 100
        cr = self.env.cr
        ids = self.ids
        while len(ids):
            cr.execute('select distinct parent_id from saas_portal_category where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                raise Warning('Error! You cannot create recursive Categories')
            level -= 1
        return True


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    category_ids = fields.Many2many(
        'saas.portal.category',
        string='Tags'
    )

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if vals.get('plan_id'):
            plan = self.env['saas_portal.plan'].browse(vals['plan_id'])
            vals['category_ids'] = [(6, 0, plan.category_ids.ids)]
        return super(SaasPortalClient, self).create(vals)


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    category_ids = fields.Many2many(
        'saas.portal.category',
        string='Client Tags'
    )
