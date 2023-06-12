# -*- coding: utf-8 -*-
{
    'name': "BI Mandatory Analytic Distribution",
    'summary': "BI Mandatory Analytic Distribution",
    'description': """  
     """,
    'author': "BI Solutions Development Team",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['base', 'sale_stock', 'purchase_stock'],
    'data': [
        'views/stock_picking_views_inherit.xml',
        'views/stock_move_views_inherit.xml',
        'views/purchase_order_views_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
