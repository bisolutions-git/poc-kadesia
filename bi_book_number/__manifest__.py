# -*- coding: utf-8 -*-
{
    'name': "BI Book Number",
    'summary': "BI Book Number",
    'description': """  
     """,
    'author': "BI Solutions Development Team",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking_views_inherit.xml',
        'views/stock_move_views_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
