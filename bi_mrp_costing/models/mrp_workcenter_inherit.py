# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MRPWorkCenter(models.Model):
    _inherit = "mrp.workcenter"

    direct_cost_ids = fields.One2many("mrp.direct.cost", "work_center_id", "Direct Cost")
    indirect_cost_ids = fields.One2many("mrp.indirect.cost", "work_center_id", "Indirect Cost")
    mrp_overhead_ids = fields.One2many("mrp.overhead", "work_center_id", "Manufacturing Overhead")
    costs_hour = fields.Float(string='Cost per hour', help='Specify cost of work center per hour.', default=0.0,
                              compute='calc_hour_cost', store=True)
    total_hour_cost = fields.Float(string='Total', compute='calc_hour_cost')

    @api.depends("direct_cost_ids", "direct_cost_ids.hour_amount",
                 "indirect_cost_ids", "indirect_cost_ids.hour_amount",
                 "mrp_overhead_ids", "mrp_overhead_ids.hour_amount")
    def calc_hour_cost(self):
        for rec in self:
            total_direct = sum(x.hour_amount for x in rec.direct_cost_ids)
            total_indirect = sum(x.hour_amount for x in rec.indirect_cost_ids)
            total_overhead = sum(x.hour_amount for x in rec.mrp_overhead_ids)
            rec.costs_hour = total_direct + total_indirect + total_overhead
            rec.total_hour_cost = total_direct + total_indirect + total_overhead
