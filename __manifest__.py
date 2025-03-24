{
    'name': 'Sales Order Validation',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'ตรวจสอบการสร้าง Sales Order ก่อนยืนยัน',
    'description': """
        โมดูลนี้จะตรวจสอบว่าการสร้าง Sales Order จะต้องมีการเลือก Quotation Template และ Route ก่อนที่จะยืนยัน
        หากไม่เลือกจะไม่สามารถยืนยัน Sales Order ได้
    """,
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/warning_message_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'application': False,
} 