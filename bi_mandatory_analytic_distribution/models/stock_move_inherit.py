# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',
                                          compute='_compute_analytic_account_id', readonly=False, store=True)

    @api.depends('picking_id.analytic_account_id', 'purchase_line_id.analytic_distribution')
    def _compute_analytic_account_id(self):
        for record in self:
            if record.picking_id and record.picking_id.analytic_account_id:
                record.analytic_account_id = record.picking_id.analytic_account_id.id
            elif record.purchase_line_id and record.purchase_line_id.analytic_distribution:
                record.analytic_account_id = int(list(record.purchase_line_id.analytic_distribution.keys())[0])


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project',
                                          related='move_id.analytic_account_id', readonly=False, store=True)
