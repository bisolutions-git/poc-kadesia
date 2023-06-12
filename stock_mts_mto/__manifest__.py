{
    'name': 'Stock MTS+MTO Enhancements',
    'version': '1.1',
    'category': 'Sales',
    'depends': ['account', 'sale', 'product', 'purchase', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'data/stock_data.xml',
    ],

}
