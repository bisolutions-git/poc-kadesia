{
    'name': "BI Product Card Report",
    'summary': "BI Product Card Report",
    'description': """ 
            This module generates xlsx reports to product card.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['stock', 'sale', 'purchase', 'bi_mandatory_analytic_distribution', 'bi_book_number', 'report_xlsx'],
    'data': ['views/wizard_view.xml', 'security/ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
}
