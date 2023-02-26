from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    delivered_items_price = fields.Float(string="Delivered Items Price", compute="get_delivered_items_price",
                                         store=False)

    alternative_partner_id = fields.Many2one(
        'res.partner', string='Alternative Partner', readonly=False,
        index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        default=lambda self: self.partner_id.id
    )

    @api.onchange('partner_id')
    def set_alternative_partner_id(self):
        self.alternative_partner_id = self.partner_id.id

    @api.model
    def create_batch_payment(self):
        # We use self[0] to create the batch; the constrains on the model ensure
        # the consistency of the generated data (same journal, same payment method, ...)
        if any([p.payment_type == 'transfer' for p in self]):
            raise UserError(
                _('You cannot make a batch payment with internal transfers. Internal transfers ids: %s')
                % ([p.id for p in self if p.payment_type == 'transfer'])
            )

        # batch = self.env['account.batch.payment'].create({
        #     'journal_id': self[0].journal_id.id,
        #     'payment_ids': [(4, payment.id, None) for payment in self],
        #     'payment_method_id': self[0].payment_method_id.id,
        #     'batch_type': self[0].payment_type,
        #     'alternative_partner_id': self[0].alternative_partner_id.id,
        # })

        # return {
        #     "type": "ir.actions.act_window",
        #     "res_model": "account.batch.payment",
        #     "views": [[False, "form"]],
        #     "res_id": batch.id,
        # }
