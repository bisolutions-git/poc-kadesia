# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price', groups="hide_cost_price.group_show_sales_price",
        help="Price at which the product is sold to customers.",
    )

    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="hide_cost_price.group_show_cost_price",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
