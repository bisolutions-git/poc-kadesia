# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MRPOverhead(models.Model):
    _name = "mrp.overhead"
    _description = "MRP Overhead"
    _rec_name = "account_id"

    hour_amount = fields.Monetary("Amount/hour")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    account_id = fields.Many2one("account.account", "Account")
    work_center_id = fields.Many2one("mrp.workcenter")
    analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account")
