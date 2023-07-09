# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpWorkorderInherit(models.Model):
    _inherit = 'mrp.workorder'

    has_access_to_duration = fields.Boolean(string="Has Access To Duration", compute='_compute_has_access_to_duration')

    def _compute_has_access_to_duration(self):
        for record in self:
            record.has_access_to_duration = self.env.user.has_group(
                'bi_mrp_access_rights.edit_work_order_duration_group')
