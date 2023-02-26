from odoo import models, fields, api
from datetime import datetime, date


class CustomerBalanceReport(models.TransientModel):
    _name = "wizard.customer.balance.report"
    _description = "Customer Balance Report"

    def _get_default_start_date(self):
        year = date.today().year
        first_of_year = date(year=year, month=1, day=1)
        return first_of_year

    def _get_default_end_date(self):
        return date.today()

    # def _get_default_currency(self):
    #     return self.env.user.company_id.currency_id

    def _get_default_companies(self):
        return self.env.company

    start_date = fields.Date(string="Start Date", required=True, default=_get_default_start_date)
    end_date = fields.Date(string="End Date", required=True, default=_get_default_end_date)
    currency_ids = fields.Many2one('res.currency', string="Currency", required=True,
                                    default=lambda self: self.env.user.company_id.currency_id.id)
    customer_ids = fields.Many2many('res.partner', string="Customers", domain=[('customer_rank', '>', 0)])
    company_id = fields.Many2many('res.company', string="Company", required=True, default=_get_default_companies)
    report_type = fields.Selection([('xlsx', 'Excel'), ('pdf', 'PDF')], string="Report Type", default='xlsx',
                                   required=True)
    show_section = fields.Boolean(string="Show Section", default=True)

    def get_customer_lines(self, data, customer_ids, currency, parent=False):
        company = self.company_id
        lines = list()
        end_date = datetime(year=data['end_date'].year, month=data['end_date'].month, day=data['end_date'].day,
                            hour=23, minute=59, second=59)
        # Get Pickings
        orders = self.sudo().env['sale.order'].search([
            ('alternative_partner_id', 'in', customer_ids),
            ('company_id', 'in', company.ids),
            ('currency_id', '=', self.currency_ids.id)
        ]).ids
        pickings = self.sudo().env['stock.picking'].search([
            ('date_done', '<=', end_date),
            ('state', '=', 'done'),
            ('sale_id', 'in', orders)
        ])
        for pick in pickings:
            amount, currency = pick.get_value()
            lines.append({
                'date': pick.date_done.date(),
                'reference': pick.name,
                'amount': -amount if pick.picking_type_code != 'outgoing' else amount,
                'balance': 0.0,
                'checks': 0.0,
                'type': 'pick',
                'child_name': '--',
                'is_foreign': False,
                'foreign_amount': amount,
                'foreign_currency': self.currency_ids.name,
                'company': pick.company_id.name
            })
        # Get Payments
        payments = self.sudo().env['account.payment'].search([
            ('date', '<=', data['end_date']),
            ('alternative_partner_id', 'in', customer_ids),
            ('company_id', 'in', company.ids),
            ('state', 'not in', ['draft', 'cancelled']),
            ('currency_id', '=', self.currency_ids.id),
        ])
        for payment in payments:
            lines.append({
                'date': payment.date,
                'reference': payment.name,
                'amount': payment.amount * (-1 if payment.payment_type == 'outbound' else 1),
                'balance': 0.0,
                'checks': 0.0,
                'type': 'payment',
                'child_name': payment.alternative_partner_id.name if parent and payment.alternative_partner_id.id != parent.id else '--',
                'is_foreign': False,
                'foreign_amount': payment.amount * (-1 if payment.payment_type == 'outbound' else 1),
                'foreign_currency': currency.name,
                'company': payment.company_id.name
            })
        lines.sort(key=lambda x: (x['date'], x['reference']), reverse=False)
        balance = 0
        for line in lines:
            line['show'] = True if self.start_date <= line['date'] <= self.end_date else False
            line['start_balance'] = balance
            balance += line['amount'] if line['type'] == 'pick' else -line['amount'] if line['type'] == 'payment' else 0
            line['balance'] = balance
            # line['checks'] = 0.0

        return lines

    def get_sections(self, currency):
        data = dict()
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date

        lines = list()
        p_c_ids = list()
        customers = self.env['res.partner'].search([
            ('customer_rank', '>', 0)
        ])
        if self.customer_ids:
            parent_customers = self.customer_ids.filtered(lambda cu: cu.child_ids is not False)
        else:
            parent_customers = self.env['res.partner'].search([
                ('child_ids', '!=', False),
                ('customer_rank', '>', 0)
            ])
        for customer in parent_customers:
            customer_ids = [customer.id]
            customer_ids += customer.child_ids.ids
            customer_lines = self.get_customer_lines(data, customer_ids, currency, parent=customer)
            if customer_lines:
                lines.append({
                    'customer': customer,
                    'data': customer_lines,
                    'currency': currency.name
                })
            p_c_ids += customer_ids

        if self.customer_ids:
            child_customers = self.customer_ids - parent_customers
        else:
            child_customers = customers - parent_customers

        for customer in child_customers:
            if customer.id in p_c_ids:
                continue
            customer_ids = [customer.id]
            customer_ids += customer.child_ids.ids
            customer_lines = self.get_customer_lines(data, customer_ids, currency)
            if customer_lines:
                lines.append({
                    'customer': customer,
                    'data': customer_lines,
                    'currency': currency.name
                })
        return lines

    def get_report_currency(self):
        return self.currency_id.name

    # def get_uncollected_checks(self, customer_id, currency):
    #     amount = 0.0
    #     customer_ids = customer_id.child_ids.ids
    #     customer_ids.append(customer_id.id)
    #     batch_payments = self.sudo().env['account.batch.payment'].search([
    #         ('date', '<=', self.end_date),
    #         ('alternative_partner_id', 'in', customer_ids),
    #         ('batch_type', '=', 'inbound'),
    #         ('state', 'in', ['draft', 'sent', 'under_collection']),
    #         ('currency_id', '=', currency.id),
    #     ])
    #     for batch_payment in batch_payments:
    #         amount += sum(
    #             payment.amount
    #             for payment in batch_payment.payment_ids
    #         )
    #     return amount

    def export_report(self):
        if self.report_type == 'xlsx':
            return self.sudo().env.ref('bi_daily_customer_balance.customer_balance_xlsx').report_action(docids=self.id)
        else:
            return self.sudo().env.ref('bi_daily_customer_balance.customer_balance_pdf').report_action(docids=self.id)
