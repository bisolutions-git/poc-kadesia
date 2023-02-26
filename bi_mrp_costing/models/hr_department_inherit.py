# -*- coding: utf-8 -*-

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = "hr.department"

    display_in_work_centers = fields.Boolean('Display In Work Centers')
