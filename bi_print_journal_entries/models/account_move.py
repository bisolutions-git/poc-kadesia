# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JournalEntryReport(models.Model):
    _inherit = 'account.move'

    total_debit = fields.Monetary(compute='_compute_total_debit')
    total_credit = fields.Monetary(compute='_compute_total_credit')

    accountant_id = fields.Many2one('res.users', string='Accountant')
    account_manager_id = fields.Many2one('res.users', string='Account Manager')

    def _compute_total_debit(self):
        for record in self:
            total = 0
            for line in record.line_ids:
                total = total + line.debit
            record.total_debit = total

    def _compute_total_credit(self):
        for record in self:
            total = 0
            for line in record.line_ids:
                total = total + line.credit
            record.total_credit = total

    def _post(self, soft=True):
        for record in self:
            record.accountant_id = self.env.user.id

        return super(JournalEntryReport, self)._post(soft)

    def button_set_checked(self):
        for record in self:
            record.account_manager_id = self.env.user.id

        return super(JournalEntryReport, self).button_set_checked()

    def print_journal_entry(self):
        return self.env.ref('bi_print_journal_entries.action_report_journal_entry').report_action(self)


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    exchange_rate = fields.Float(compute='_compute_exchange_rate', store=True)

    @api.depends('amount_currency', 'debit', 'credit')
    def _compute_exchange_rate(self):
        for record in self:
            rate = 0
            if record.debit != 0 and record.amount_currency != 0:
                rate = record.debit / record.amount_currency
            elif record.credit != 0 and record.amount_currency != 0:
                rate = record.credit / record.amount_currency

            if rate < 0:
                rate = rate * -1

            record.exchange_rate = rate


class JournalEntryReportInPayment(models.Model):
    _inherit = 'account.payment'

    def get_data(self):
        records = self.env['account.move'].search([])
        items = []
        move_record = []

        for record in records:
            ids = set()
            for line in record.line_ids:
                ids.add(line.id)
            item = (ids, record.id)
            items.append(item)

        my_lines = self.move_line_ids

        if len(my_lines) == 2:
            my_ids = set()
            for line in my_lines:
                my_ids.add(line.id)

            for item in items:
                if item[0] == my_ids:
                    move_record.append(self.env['account.move'].search([('id', '=', item[1])]))
        else:
            lines_info = []
            my_ids = []

            for line in my_lines:
                lines_info.append((line.id, line.move_id.id))

            if lines_info[0][1] == lines_info[1][1]:
                my_ids.append({lines_info[0][0], lines_info[1][0]})
                my_ids.append({lines_info[2][0], lines_info[3][0]})
            elif lines_info[0][1] == lines_info[2][1]:
                my_ids.append({lines_info[0][0], lines_info[2][0]})
                my_ids.append({lines_info[1][0], lines_info[3][0]})
            elif lines_info[0][1] == lines_info[3][1]:
                my_ids.append({lines_info[0][0], lines_info[3][0]})
                my_ids.append({lines_info[1][0], lines_info[2][0]})

            for item in items:
                if item[0] == my_ids[0] or item[0] == my_ids[1]:
                    move_record.append(self.env['account.move'].search([('id', '=', item[1])]))

        return move_record
