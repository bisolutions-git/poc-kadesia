# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',
                                          compute='_compute_analytic_account_id', readonly=False, store=True)

    @api.depends('sale_id.analytic_account_id')
    def _compute_analytic_account_id(self):
        for record in self:
            if record.sale_id and record.sale_id.analytic_account_id:
                record.analytic_account_id = record.sale_id.analytic_account_id.id
