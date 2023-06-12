# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    book_no = fields.Char(string='Book No.')


