# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    unit_cost = fields.Float(string='Unit Cost', compute='_compute_unit_cost')

    def _compute_unit_cost(self):
        for record in self:
            currency_table = self.env['res.currency']._get_query_currency_table(
                {'multi_company': True, 'date': {'date_to': fields.Date.today()}})
            product = record.product_id

            total_cost_operations = 0.0
            Workorders = self.env['mrp.workorder'].search([('production_id', '=', self.id)])
            if Workorders:
                query_str = """SELECT
                                    wo.duration,
                                    CASE WHEN wo.costs_hour = 0.0 THEN wc.costs_hour ELSE wo.costs_hour END AS costs_hour,
                                    currency_table.rate
                               FROM mrp_workcenter_productivity t
                               LEFT JOIN mrp_workorder wo ON (wo.id = t.workorder_id)
                               LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id)
                               LEFT JOIN {currency_table} ON currency_table.company_id = t.company_id
                               WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                               GROUP BY wo.production_id, wo.id, wo.name, wc.costs_hour, wc.name, t.user_id, currency_table.rate
                               ORDER BY wo.name, wc.name
                                   """.format(currency_table=currency_table, )
                self.env.cr.execute(query_str, (tuple(Workorders.ids),))
                for duration, cost_hour, currency_rate in self.env.cr.fetchall():
                    cost = duration / 60.0 * cost_hour * currency_rate
                    total_cost_operations += cost

            total_cost_components = 0.0
            query_str = """SELECT 
                                abs(SUM(svl.value)),
                                currency_table.rate
                           FROM stock_move AS sm
                           INNER JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                           LEFT JOIN mrp_production AS mo on sm.raw_material_production_id = mo.id
                           LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
                           WHERE sm.raw_material_production_id = %s AND sm.state != 'cancel' AND sm.product_qty != 0 AND scrapped != 't'
                           GROUP BY sm.product_id, mo.id, currency_table.rate""".format(currency_table=currency_table, )
            self.env.cr.execute(query_str, (record.id,))
            for cost, currency_rate in self.env.cr.fetchall():
                cost *= currency_rate
                total_cost_components += cost

            qty = sum(
                record.move_finished_ids.filtered(lambda mo: mo.state == 'done' and mo.product_id == product).mapped(
                    'product_uom_qty'))
            if record.product_uom_id.id == product.uom_id.id:
                mo_qty = qty
            else:
                mo_qty = record.product_uom_id._compute_quantity(qty, product.uom_id)

            if mo_qty:
                record.unit_cost = (total_cost_components + total_cost_operations) / mo_qty
            else:
                record.unit_cost = 0
