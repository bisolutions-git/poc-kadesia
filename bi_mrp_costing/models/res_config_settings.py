# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import ast


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cost_wip_account_id = fields.Many2one('account.account', 'WIP Cost Account')
    cost_wip_journal_id = fields.Many2one('account.journal', 'WIP Cost Journal')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.company
        res['cost_wip_account_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('cost_wip_account_id_in_company_{}'.format(company.id)))
        res['cost_wip_journal_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('cost_wip_journal_id_in_company_{}'.format(company.id)))
        return res

    @api.model
    def set_values(self):
        company = self.env.company
        self.env['ir.config_parameter'].sudo().set_param('cost_wip_account_id_in_company_{}'.format(company.id),
                                                         self.cost_wip_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('cost_wip_journal_id_in_company_{}'.format(company.id),
                                                         self.cost_wip_journal_id.id)
        return super(ResConfigSettings, self).set_values()
