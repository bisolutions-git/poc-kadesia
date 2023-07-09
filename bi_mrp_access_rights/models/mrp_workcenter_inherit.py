# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpWorkcenterInherit(models.Model):
    _inherit = 'mrp.workcenter'

    department_ids = fields.Many2many('hr.department', string='Departments')
