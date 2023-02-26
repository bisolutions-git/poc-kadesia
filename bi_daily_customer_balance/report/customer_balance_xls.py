from datetime import datetime, date
from odoo import models, fields, _
import pytz


class StandardReportXlsx(models.AbstractModel):
    _name = 'report.bi_daily_customer_balance.report_customer_balance_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        for currency in objs.currency_ids:
            sections = objs.get_sections(currency)
            sheet = workbook.add_worksheet(currency.name)
            format1 = workbook.add_format(
                {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
                 'bold': True})
            format21 = workbook.add_format(
                {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
                 'bold': True})
            format21_unbolded = workbook.add_format(
                {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
                 'bold': False, 'num_format': '#,##0.00'})
            format_left_align_left = workbook.add_format(
                {'font_size': 10, 'align': 'left', 'right': False, 'left': True, 'bottom': True, 'top': True,
                 'bold': True})
            format_left_align_right = workbook.add_format(
                {'font_size': 10, 'align': 'left', 'right': True, 'left': False, 'bottom': True, 'top': True,
                 'bold': True})
            format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
            font_size_8 = workbook.add_format(
                {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
            red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                            'bg_color': 'red'})
            justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
            border = workbook.add_format(
                {'bottom': False, 'top': False, 'right': False, 'left': False, 'bg_color': 'gray',
                 'font_size': 10, 'align': 'center', 'bold': True})
            format3.set_align('center')
            font_size_8.set_align('center')
            justify.set_align('justify')
            format1.set_align('center')
            red_mark.set_align('center')
            user = self.env['res.users'].browse(self.env.uid)
            tz = pytz.timezone(user.tz if user.tz else 'UTC')
            times = pytz.utc.localize(datetime.now()).astimezone(tz)
            sheet.merge_range('A1:D3', 'Report Date: ' + str(times.strftime("%Y-%m-%d %I:%M %p")), format1)
            sheet.write(0, 4, 'From: ', format_left_align_left)
            sheet.merge_range('F1:G1', datetime.strftime(objs.start_date, "%Y-%m-%d"), format_left_align_right)
            sheet.write(1, 4, 'To: ', format_left_align_left)
            sheet.merge_range('F2:G2', datetime.strftime(objs.end_date, "%Y-%m-%d"), format_left_align_right)

            if objs.show_section:
                sheet.set_column(0, 0, 15)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 15)
                sheet.set_column(3, 3, 12)
                sheet.set_column(4, 4, 12)
                sheet.set_column(5, 5, 12)
                sheet.set_column(6, 6, 18)
                sheet.set_column(7, 7, 15)
            else:
                sheet.set_column(0, 0, 30)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 15)
                sheet.set_column(3, 3, 15)
                sheet.set_column(4, 4, 12)
                sheet.set_column(5, 5, 12)
                sheet.set_column(6, 6, 12)
                sheet.set_column(7, 7, 18)
                sheet.set_column(8, 8, 15)

            count = 3
            sheet.merge_range('A' + str(count + 1) + (':H' if objs.show_section else ':G') + str(count + 1), "", border)
            count += 1
            total_start_balance, total_end_balance, total_sales, total_payments = 0.0, 0.0, 0.0, 0.0
            if not objs.show_section:
                sheet.write(count, 0, "Customer", format21)
                sheet.write(count, 1, "Date", format21)
                sheet.write(count, 2, "Reference", format21)
                sheet.write(count, 3, "Start Balance", format21)
                sheet.write(count, 4, "Sales", format21)
                sheet.write(count, 5, "Payment", format21)
                sheet.write(count, 6, "End Balance", format21)
                # sheet.write(count, 7, "Uncollected Checks", format21)
                count += 1
            for section in sections:
                flag = 0
                if objs.show_section:
                    sheet.merge_range('A' + str(count + 1) + ':I' + str(count + 1),
                                      section['customer'].name + " Balance in " + section['currency'], format21)
                    count += 1
                    sheet.merge_range('A' + str(count + 1) + ':I' + str(count + 1),
                                      "Limit:  " + str(section['customer'].credit_limit), format21)
                    count += 1
                    sheet.write(count, 0, "Date", format21)
                    sheet.write(count, 1, "Reference", format21)
                    sheet.write(count, 2, "Start Balance", format21)
                    sheet.write(count, 3, "Sales", format21)
                    sheet.write(count, 4, "Payment", format21)
                    sheet.write(count, 5, "End Balance", format21)
                    # sheet.write(count, 6, "Uncollected Checks", format21)
                    # sheet.write(count, 7, "Child Name", format21)
                    # sheet.write(count, 8, "Company", format21)
                    count += 1
                start_balance, end_balance, sales, payments = 0.0, 0.0, 0.0, 0.0
                for i, line in enumerate(section['data']):
                    if line['show']:
                        end_balance = line['balance']
                        if (i == 0):
                            start_balance = line['start_balance']
                        if line['type'] == 'pick':
                            sales += line['amount']
                        elif line['type'] == 'payment':
                            payments += line['amount']
                        if not objs.show_section:
                            flag = 1
                            continue

                        sheet.write(count, 0, datetime.strftime(line['date'], "%Y-%m-%d "), format21_unbolded)
                        sheet.write(count, 1, line['reference'], format21_unbolded)
                        sheet.write(count, 2, '{0:,.2f}'.format(line['start_balance']), format21_unbolded)
                        if line['type'] == 'pick':
                            sheet.write(count, 3, '{0:,.2f}'.format(line['amount']), format21_unbolded)
                            sheet.write(count, 4, '--', format21_unbolded)
                        if line['type'] == 'payment':
                            sheet.write(count, 3, '--', format21_unbolded)
                            sheet.write(count, 4, '{0:,.2f}'.format(line['amount']), format21_unbolded)
                        sheet.write(count, 5, '{0:,.2f}'.format(line['balance']), format21_unbolded)
                        sheet.write(count, 6, '--', format21_unbolded)
                        sheet.write(count, 7, line['child_name'], format21_unbolded)
                        sheet.write(count, 8, line['company'], format21_unbolded)
                        count += 1
                    else:
                        start_balance = line['balance']
                        end_balance = line['balance']
                        if not objs.show_section:
                            flag = 1
                            continue
                total_sales += sales
                total_payments += payments
                total_start_balance += start_balance
                total_end_balance += end_balance
                if True:
                    # checks = objs.get_uncollected_checks(section['customer'], currency)
                    # total_checks += checks
                    if flag:
                        sheet.write(count, 0, section['customer'].name, format21_unbolded)
                    line_format = format21 if objs.show_section else format21_unbolded
                    sheet.write(count, 0 + flag, datetime.strftime(objs.end_date, "%Y-%m-%d "), line_format)
                    sheet.write(count, 1 + flag, "--", line_format)
                    sheet.write(count, 2 + flag, '{0:,.2f}'.format(start_balance), line_format)
                    sheet.write(count, 3 + flag, '{0:,.2f}'.format(sales), line_format)
                    sheet.write(count, 4 + flag, '{0:,.2f}'.format(payments), line_format)
                    sheet.write(count, 5 + flag, '{0:,.2f}'.format(end_balance), line_format)
                    # sheet.write(count, 6 + flag, '{0:,.2f}'.format(checks), line_format)
                    if not flag:
                        sheet.write(count, 7, '--', format21_unbolded)
                    count += 1
                if objs.show_section:
                    sheet.merge_range('A' + str(count + 1) + ':I' + str(count + 1), "", border)
                    count += 1
