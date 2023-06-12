# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    book_no = fields.Char(string='Book No.', related='picking_id.book_no', store=True)


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    book_no = fields.Char(string='Book No.', related='move_id.book_no', store=True)
