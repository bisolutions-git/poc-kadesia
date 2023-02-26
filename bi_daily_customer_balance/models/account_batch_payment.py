from odoo import models, fields, api, _


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    def get_default_alternative_partner(self):
        result = False
        if self.payment_ids:
            result = self.payment_ids[0].partner_id.id
        return result

    alternative_partner_id = fields.Many2one(
        'res.partner', string='Alternative Partner',
        required=True,
        index=True,
        default=lambda x: x.get_default_alternative_partner()
    )

    @api.depends('payment_ids', 'payment_ids.alternative_partner_id')
    def get_lines_data(self):
        super(AccountBatchPayment, self).get_lines_data()
        for record in self:
            if record.payment_ids:
                record.update({'alternative_partner_id': record.payment_ids[0].alternative_partner_id.id})
            else:
                record.update({'alternative_partner_id': False})
