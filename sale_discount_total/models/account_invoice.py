# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Faslu Rahman(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.move"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=(16, 2),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')
    discount_method = fields.Selection([('global', 'Global'), ('line', 'Per Line')], string='Discount Method',
                                       readonly=True, default='global',
                                       states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state',
        'discount_type',
        'discount_rate')
    def _compute_amount(self):
        res = super(AccountInvoice, self)._compute_amount()
        for move in self:
            move.amount_discount = sum(
                (line.quantity * line.price_unit * line.discount) / 100 for line in move.invoice_line_ids)
        return res

    @api.onchange('discount_method')
    def _onchange_discount_method(self):
        self.discount_rate = 0
        self.supply_rate()
        for line in self.invoice_line_ids:
            line.discount_rate = 0
            line.supply_rate()

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def supply_rate(self):
        for inv in self:
            if inv.discount_method == 'global':
                if inv.discount_type == 'percent':
                    for line in inv.invoice_line_ids:
                        line.discount = inv.discount_rate
                        line._compute_totals()
                else:
                    total = 0.0
                    for line in inv.invoice_line_ids:
                        total += (line.quantity * line.price_unit)
                    if inv.discount_rate and total:
                        discount = (inv.discount_rate / total) * 100
                    else:
                        discount = inv.discount_rate
                    for line in inv.invoice_line_ids:
                        line.discount = discount
                        line._compute_totals()

                inv._compute_tax_totals()

    def button_dummy(self):
        self.supply_rate()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'))

    @api.onchange('discount_type', 'discount_rate', 'price_unit', 'quantity')
    def supply_rate(self):
        if self.move_id.discount_method == 'line':
            if self.discount_type == 'percent':
                self.discount = self.discount_rate
            else:
                total = (self.quantity * self.price_unit)
                if self.discount_rate and total:
                    discount = (self.discount_rate / total) * 100
                else:
                    discount = self.discount_rate
                self.discount = discount
