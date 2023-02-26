# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    mrp_id = fields.Many2one("mrp.production", "Manufacturing Order")
