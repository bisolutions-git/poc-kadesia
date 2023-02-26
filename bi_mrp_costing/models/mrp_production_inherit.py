# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    workcenter_ids = fields.Many2many("mrp.workcenter", compute="get_related_workcenter")

    def get_related_workcenter(self):
        for rec in self:
            workcenter = []
            for workorder in rec.workorder_ids:
                if workorder.workcenter_id:
                    workcenter.append(workorder.workcenter_id.id)
            rec.workcenter_ids = [(6, 0, workcenter)]

    def _post_inventory(self, cancel_backorder=False):
        for rec in self:
            rec.action_create_cost_entry()
        res = super(MRPProduction, self)._post_inventory(cancel_backorder)
        return res

    def action_create_cost_entry(self):
        for rec in self:
            accounts = {}
            analytic_accounts = {}
            move_lines = []
            company = self.env.company
            debit_account = int(self.env['ir.config_parameter'].sudo().get_param(
                'cost_wip_account_id_in_company_{}'.format(company.id)))
            journal = int(self.env['ir.config_parameter'].sudo().get_param(
                'cost_wip_journal_id_in_company_{}'.format(company.id)))
            if not debit_account:
                raise ValidationError('Please Add WIP Cost Account In Manufacturing Configuration!')
            if not journal:
                raise ValidationError('Please Add WIP Cost Journal In Manufacturing Configuration!')
            for workorder in rec.workorder_ids:
                time_lines = workorder.time_ids.filtered(lambda x: x.date_end and not x.cost_already_recorded)
                duration = sum(time_lines.mapped('duration'))

                if workorder.workcenter_id:
                    for line in workorder.workcenter_id.direct_cost_ids:
                        if line.account_id.id not in accounts.keys():
                            accounts[line.account_id.id] = round((duration / 60.0) * line.hour_amount, 2)
                            analytic_accounts[
                                line.account_id.id] = line.analytic_account_id.id if line.analytic_account_id else False
                        else:
                            accounts[line.account_id.id] += round((duration / 60.0) * line.hour_amount, 2)

                    for line in workorder.workcenter_id.indirect_cost_ids:
                        if line.account_id.id not in accounts.keys():
                            accounts[line.account_id.id] = round((duration / 60.0) * line.hour_amount, 2)
                            analytic_accounts[
                                line.account_id.id] = line.analytic_account_id.id if line.analytic_account_id else False
                        else:
                            accounts[line.account_id.id] += round((duration / 60.0) * line.hour_amount, 2)

                    for line in workorder.workcenter_id.mrp_overhead_ids:
                        if line.account_id.id not in accounts.keys():
                            accounts[line.account_id.id] = round((duration / 60.0) * line.hour_amount, 2)
                            analytic_accounts[
                                line.account_id.id] = line.analytic_account_id.id if line.analytic_account_id else False
                        else:
                            accounts[line.account_id.id] += round((duration / 60.0) * line.hour_amount, 2)
            total = 0
            if accounts:
                for account in accounts:
                    total += accounts[account]
                    move_lines.append((0, 0, {
                        'name': rec.display_name,
                        'account_id': account,
                        'analytic_distribution': {str(analytic_accounts[account]): 100},
                        'credit': accounts[account],
                        'debit': 0,
                    }))
                move_lines.append((0, 0, {
                    'name': rec.display_name,
                    'account_id': debit_account,
                    'credit': 0,
                    'debit': total,
                }))
                move_id = self.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'mrp_id': rec.id,
                    'ref': rec.display_name,
                    'line_ids': move_lines,
                })
                move_id._post()

    def action_open_journals(self):
        self.ensure_one()
        action_ref = self.env.ref('account.action_account_moves_all')
        if not action_ref:
            return False
        action_data = action_ref.read()[0]
        action_data['domain'] = ['|', ('move_id.mrp_id', '=', self.id), ('move_id.ref', 'ilike', self.display_name)]
        action_data['context'] = {}
        return action_data
