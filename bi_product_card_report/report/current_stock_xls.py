from datetime import datetime
from odoo import models, _
import pytz

import logging

_logger = logging.getLogger(__name__)


class StandardReportXlsx(models.AbstractModel):
    _name = 'report.bi_product_card_report.report_product_card_excel'
    _inherit = 'report.report_xlsx.abstract'

    def get_balance(self, data):
        locations = tuple(data['locations'])
        self.env.cr.execute(
            """WITH
                source as (select t1.product_id, sum(t1.qty_done) as openin from stock_move_line as t1
                where (t1.location_dest_id in %s)
                and t1.date < %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id ),
                
                dist as (select t1.product_id, sum(t1.qty_done) as openout from stock_move_line as t1
                where (t1.location_id in %s)
                and t1.date < %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id),

                qtyin as (select t1.product_id, sum(t1.qty_done) as qtyin from stock_move_line as t1
                where (t1.location_dest_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id ),

                qtyout as (select t1.product_id, sum(t1.qty_done) as qtyout from stock_move_line as t1
                where (t1.location_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id)

                select (coalesce(source.openin,0) - coalesce(dist.openout,0)) as openBlance
                from dist full join source on dist.product_id = source.product_id
                full join qtyin on qtyin.product_id = source.product_id
                full join qtyout on qtyout.product_id = source.product_id
                left join product_product on product_product.id = GREATEST(dist.product_id,source.product_id,qtyin.product_id,qtyout.product_id)
                left join product_template on product_template.id = product_product.product_tmpl_id
                order by product_template.name""", (
                locations, data['start_date'], data['product'],
                locations, data['start_date'], data['product'],
                locations, data['start_date'], data['end_date'], data['product'],
                locations, data['start_date'], data['end_date'], data['product']))
        balances = self.env.cr.fetchall()
        return balances

    def get_lines(self, data):
        locations = tuple(data['locations'])
        self.env.cr.execute(
            """
          select 
                t2.reference, 
                t1.qty_done, 
                t1.location_id, 
                t1.location_dest_id, 
                t1.analytic_account_id, 
                t1.date,
                t1.book_no,
                t4.name 
            from 
                stock_move_line as t1 
                left join stock_move as t2 on t1.move_id = t2.id 
                left join stock_picking as t3 on t2.picking_id = t3.id
                left join res_partner as t4 on t3.partner_id = t4.id
            where 
                (t1.location_dest_id in %s or t1.location_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
            order by t1.date;
            """, (
                locations, locations,
                data['start_date'], data['end_date'],
                data['product'])
        )
        lines = self.env.cr.fetchall()
        print(lines)
        return lines

    def generate_xlsx_report(self, workbook, data, objs):
        balances = self.get_balance(data)
        lines = self.get_lines(data)
        sheet = workbook.add_worksheet('Product Info')
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
             'bold': True})
        format11 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21_unbolded = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': False})
        format_left_align_left = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': False, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format_left_align_right = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': True, 'left': False, 'bottom': True, 'top': True,
             'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
        red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                        'bg_color': 'red'})
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
        format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')

        tz = pytz.timezone(self.env.user.tz or 'UTC')
        current_date = pytz.UTC.localize(datetime.now()).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
        start_date = pytz.UTC.localize(datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M:%S")).astimezone(
            tz).replace(tzinfo=None)
        end_date = pytz.UTC.localize(datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S")).astimezone(tz).replace(
            tzinfo=None)

        if data['lang'] == 'en':
            sheet.merge_range('A1:E3', 'Report Date: ' + str(current_date), format1)
            sheet.write(0, 5, 'From: ', format_left_align_left)
            sheet.merge_range('G1:K1', str(start_date), format_left_align_right)
            sheet.write(1, 5, 'To: ', format_left_align_left)
            sheet.merge_range('G2:K2', str(end_date), format_left_align_right)
            if data['locations_names']:
                sheet.write(2, 5, 'Locations: ', format_left_align_left)
                sheet.merge_range('G3:K3', data['locations_names'][:-2], format_left_align_right)
        else:
            sheet.merge_range('A1:E3', str(current_date) + ' :تاريخ التقرير', format1)
            sheet.write(0, 5, ' :من', format_left_align_left)
            sheet.merge_range('G1:K1', str(start_date), format_left_align_right)
            sheet.write(1, 5, ' :الي', format_left_align_left)
            sheet.merge_range('G2:K2', str(end_date), format_left_align_right)
            if data['locations_names']:
                sheet.write(2, 5, ' :المخازن', format_left_align_left)
                sheet.merge_range('G3:K3', data['locations_names'][:-2], format_left_align_right)

        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)

        sheet.merge_range('B4:G4', data['product_name'], format21)

        if data['lang'] == 'en':
            sheet.write(3, 0, "Product", format21)
            sheet.write(4, 0, "Reference", format21)
            sheet.write(4, 1, "Date", format21)
            sheet.write(4, 2, "Book NO", format21)
            sheet.write(4, 3, "From", format21)
            sheet.write(4, 4, "To", format21)
            sheet.write(4, 5, "Project", format21)
            sheet.write(4, 6, "Partner", format21)
            sheet.write(4, 7, "Open Balance", format21)
            sheet.write(4, 8, "Qty In", format21)
            sheet.write(4, 9, "Qty Out", format21)
            sheet.write(4, 10, "End Balance", format21)
        else:
            sheet.write(3, 0, "الصنف", format21)
            sheet.write(4, 0, "المرجع", format21)
            sheet.write(4, 1, "التاريخ", format21)
            sheet.write(4, 2, "الرقم الدفتري", format21)
            sheet.write(4, 3, "من", format21)
            sheet.write(4, 4, "الي", format21)
            sheet.write(4, 5, "المشروع", format21)
            sheet.write(4, 6, "الجهة", format21)
            sheet.write(4, 7, "رصيد أول المدة", format21)
            sheet.write(4, 8, "الوارد", format21)
            sheet.write(4, 9, "الصادر", format21)
            sheet.write(4, 10, "الرصيد الحالي", format21)

        sheet.write(5, 0, '', format21_unbolded)
        sheet.write(5, 1, '', format21_unbolded)
        sheet.write(5, 2, '', format21_unbolded)
        sheet.write(5, 3, '', format21_unbolded)
        sheet.write(5, 4, '', format21_unbolded)
        sheet.write(5, 5, '', format21_unbolded)
        sheet.write(5, 6, '', format21_unbolded)
        if balances:
            sheet.write(5, 7, '{0:,.3f}'.format(balances[0][0]), format21)
        else:
            sheet.write(5, 7, '', format21)
        sheet.write(5, 8, '', format21_unbolded)
        sheet.write(5, 9, '', format21_unbolded)
        sheet.write(5, 10, '', format21_unbolded)

        count = 6
        _logger.info('Balance_logger')
        _logger.info(balances)
        if balances:
            open_balance = balances[0][0]
            end_balance = balances[0][0]
        else:
            open_balance = 0
            end_balance = 0
        for line in lines:
            qty_in = (line[1] if line[3] in data['locations'] else 0)
            print(line[1])
            qty_out = (line[1] if line[2] in data['locations'] else 0)
            from_location = self.env['stock.location'].browse(line[2])
            from_name = from_location[0].complete_name if from_location else '--'
            to_location = self.env['stock.location'].browse(line[3])
            to_name = to_location[0].complete_name if to_location else '--'
            project = self.env['account.analytic.account'].browse(line[4])
            end_balance = end_balance + qty_in - qty_out
            sheet.write(count, 0, line[0], format21_unbolded)
            sheet.write(count, 1, str(line[5].date()), format21_unbolded)
            sheet.write(count, 2, line[6], format21_unbolded)
            sheet.write(count, 3, from_name, format21_unbolded)
            sheet.write(count, 4, to_name, format21_unbolded)
            sheet.write(count, 5, project.display_name if project else '--', format21_unbolded)
            sheet.write(count, 6, line[7], format21_unbolded)
            sheet.write(count, 7, '{0:,.3f}'.format(open_balance), format21_unbolded)
            sheet.write(count, 8, '{0:,.3f}'.format(qty_in), format21_unbolded)
            sheet.write(count, 9, '{0:,.3f}'.format(qty_out), format21_unbolded)
            sheet.write(count, 10, '{0:,.3f}'.format(end_balance), format21_unbolded)
            open_balance = end_balance
            count += 1

        sheet.write(count, 0, '', format21_unbolded)
        sheet.write(count, 1, '', format21_unbolded)
        sheet.write(count, 2, '', format21_unbolded)
        sheet.write(count, 3, '', format21_unbolded)
        sheet.write(count, 4, '', format21_unbolded)
        sheet.write(count, 5, '', format21_unbolded)
        sheet.write(count, 6, '', format21_unbolded)
        sheet.write(count, 7, '', format21_unbolded)
        sheet.write(count, 8, '', format21_unbolded)
        sheet.write(count, 9, '', format21_unbolded)
        sheet.write(count, 10, '{0:,.3f}'.format(end_balance), format21)
