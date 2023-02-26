from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivered_items_price = fields.Float(string="Delivered Items Price", compute="get_delivered_items_price",
                                         store=False)

    alternative_partner_id = fields.Many2one(
        'res.partner', string='Alternative Customer', readonly=False,
        required=False, index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.partner_id.id
    )

    @api.onchange('partner_id')
    def set_alternative_partner_id(self):
        self.alternative_partner_id = self.partner_id.id

    def get_delivered_items_price(self):
        for record in self:
            move_lines = record.mapped('picking_ids').filtered(lambda pick: pick.state == 'done').\
                mapped('move_line_ids_without_package')
            products = {}
            total = 0.0
            for line in move_lines:
                if line.product_id.id not in products:
                    products[line.product_id.id] = 0

                pick = line.picking_id
                if pick.picking_type_code != 'outgoing':
                    products[line.product_id.id] -= line.qty_done
                else:
                    products[line.product_id.id] += line.qty_done
            for product in products:
                order_line = (record.order_line.filtered(lambda line: line.product_id.id == product))
                price = order_line[0].price_total / order_line[0].product_uom_qty
                total += price * products[product]
            record.delivered_items_price = total
