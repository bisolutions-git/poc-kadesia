# -*- coding: utf-8 -*-
{
    'name': "BI Manufacturing Cost",
    'summary': "BI Manufacturing Cost",
    'description': """ 
        This module Manufacturing Cost.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['mrp', 'hr_contract', 'mrp_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_workcenter_inherit.xml',
        'views/mrp_production_view.xml',
        'views/res_config_settings_views.xml',
        'views/hr_department_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
