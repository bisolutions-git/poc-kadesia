# -*- coding: utf-8 -*-
{
    'name': "BI MRP Access Rights",
    'summary': "BI MRP Access Rights",
    'author': "BI Solutions Development Team",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['base', 'mrp'],
    'data': [
        'security/mrp_security.xml',
        'views/mrp_production_views_inherit.xml',
        'views/mrp_workcenter_views_inherit.xml',
        'views/mrp_workorder_views_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
