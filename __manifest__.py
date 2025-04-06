{
    'name': 'Sales Order Validation',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'ตรวจสอบการสร้าง Sales Order ก่อนยืนยัน และเพิ่มฟังก์ชันการแยกที่อยู่',
    'description': """
        โมดูลนี้จะตรวจสอบว่าการสร้าง Sales Order จะต้องมีการเลือก Quotation Template และ Route ก่อนที่จะยืนยัน
        หากไม่เลือกจะไม่สามารถยืนยัน Sales Order ได้
        
        นอกจากนี้ยังมีฟังก์ชันการแยกที่อยู่อัตโนมัติ โดยสามารถวางที่อยู่ทั้งหมดในช่องเดียว
        ระบบจะแยกข้อมูลออกเป็น Street, City, State และ ZIP code โดยอัตโนมัติ
    """,
    'depends': ['sale_management', 'stock', 'base'],
    'data': [
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'application': False
} 