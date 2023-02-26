{
    'name': "BI Customer Balance Report",
    'summary': "BI Customer Balance Report",
    'description': """ 
            This module generates xlsx reports to .
     """,
    'author': "BI Solutions Development Team",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale_stock', 'stock', 'report_xlsx', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/menuitems.xml',
        'views/res_partner_form.xml',
        'views/sale_order_form.xml',
        'views/account_payment_form.xml',
        'report/reports_templates.xml',
        'report/reports.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
}
