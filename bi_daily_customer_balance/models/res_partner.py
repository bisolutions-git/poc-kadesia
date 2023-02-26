from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    def generate_customer_balance_report(self):
        self.ensure_one()
        form_view_id = self.env.ref("bi_daily_customer_balance.wizard_form").id
        return {
            "name": _("Customer Balance Report"),
            "type": 'ir.actions.act_window',
            "res_model": 'wizard.customer.balance.report',
            "views": [(form_view_id, 'form')],
            "target": 'new',
            "context": {
                'default_customer_ids': [(4, self.id)]
            }
        }
