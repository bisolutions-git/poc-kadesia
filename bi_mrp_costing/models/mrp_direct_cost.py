# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MRPDirectCost(models.Model):
    _name = "mrp.direct.cost"
    _description = "MRP Direct Cost"

    employee_id = fields.Many2one("hr.employee", "Employee")
    hour_amount = fields.Monetary("Amount/hour")
    employee_hour_amount = fields.Monetary("Employee Amount/hour", compute="calc_employee_hour_amount", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    percentage = fields.Float("%", default=100)
    account_id = fields.Many2one("account.account", "Account")
    analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account")
    work_center_id = fields.Many2one("mrp.workcenter")

    @api.depends("employee_id", "percentage", "employee_id.contract_id.wage")
    def calc_employee_hour_amount(self):
        for rec in self:
            if rec.employee_id:
                if not rec.employee_id.contract_id:
                    raise ValidationError("Employee Must Have a Contract")
                hour_wage = (rec.employee_id.contract_id.wage / 30.0) / 8.0
                rec.employee_hour_amount = round(hour_wage * rec.percentage / 100.0, 2)

    @api.onchange('employee_id', 'percentage')
    def onchange_employee_id(self):
        if self.employee_id:
            self.hour_amount = self.employee_hour_amount
            self._origin.hour_amount = self.employee_hour_amount
