# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if 'order_line' in vals:
            for line in vals['order_line']:
                if not line[2]['analytic_distribution']:
                    raise exceptions.ValidationError("Please set the analytic distribution on the lines!")

        return super(PurchaseOrderInherit, self).create(vals)
