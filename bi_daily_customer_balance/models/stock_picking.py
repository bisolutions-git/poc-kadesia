from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_value(self):
        self.ensure_one()
        move_lines = self.mapped('move_line_ids_without_package')
        products = {}
        total = 0.0
        for line in move_lines:
            if line.product_id.id in products:
                products[line.product_id.id] += line.qty_done
            else:
                products[line.product_id.id] = line.qty_done
        for product in products:
            order_line = (self.sale_id.order_line.filtered(lambda line: line.product_id.id == product))
            price = order_line[0].price_total / order_line[0].product_uom_qty
            total += price * products[product]
        return (total, self.sale_id.currency_id)
