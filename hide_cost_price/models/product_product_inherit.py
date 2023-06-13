# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    lst_price = fields.Float(
        'Sales Price', compute='_compute_product_lst_price',
        digits='Product Price', groups="hide_cost_price.group_show_sales_price", inverse='_set_product_lst_price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")

    standard_price = fields.Float(
        'Cost', company_dependent=True,
        digits='Product Price',
        groups="hide_cost_price.group_show_cost_price",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
