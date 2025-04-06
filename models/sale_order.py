from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo import fields
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    temp_full_address = fields.Text(
        string='Quick Address Entry',
        help='Paste a complete address here to create a new contact'
    )
    
    temp_contact_name = fields.Char(
        string='Contact Name',
        help='Edit the contact name here'
    )
    
    show_contact_name = fields.Boolean(
        string='Show Contact Name Field',
        default=False
    )

    @api.onchange('temp_full_address')
    def _onchange_temp_full_address(self):
        if self.temp_full_address and not self.partner_id:
            # สร้าง partner ใหม่
            partner = self.env['res.partner'].create({
                'name': 'New Contact',  # ชื่อเริ่มต้น
                'full_address': self.temp_full_address,  # ใช้ฟังก์ชัน inverse ที่มีอยู่แล้ว
                'customer_rank': 1,  # ตั้งเป็นลูกค้า
            })
            
            # อัพเดทชื่อ partner ตามที่อยู่
            if partner.street:
                default_name = f"Customer - {partner.street}"
                partner.name = default_name
                self.temp_contact_name = default_name
            
            # กำหนด partner_id
            self.partner_id = partner.id
            self.temp_full_address = False  # ล้างค่าหลังจากสร้าง partner แล้ว
            self.show_contact_name = True  # แสดงฟิลด์แก้ไขชื่อ
            
            # ส่งข้อความแจ้งเตือน
            return {
                'warning': {
                    'title': 'Contact Created',
                    'message': 'Contact created successfully! You can edit the contact name below.'
                }
            }

    @api.onchange('temp_contact_name')
    def _onchange_temp_contact_name(self):
        if self.temp_contact_name and self.partner_id:
            self.partner_id.name = self.temp_contact_name

    def action_confirm(self):
        for order in self:
            # Check if quotation template is selected
            if not order.sale_order_template_id:
                raise ValidationError(_('กรุณาเลือก เทมเพลตใบเสนอราคา ก่อนยืนยันคำสั่งขาย\nPlease select a Quotation Template before confirming the order.'))
            
            # Check if all order lines have routes selected
            lines_without_route = order.order_line.filtered(lambda l: not l.route_id and l.product_id.type != 'service')
            if lines_without_route:
                raise ValidationError(_('กรุณาเลือก เส้นทางการขนส่ง สำหรับรายการสินค้าต่อไปนี้ก่อนยืนยันคำสั่งขาย:\n%s\n\nPlease select a Route for the following products before confirming the order:\n%s') % 
                    ('\n'.join(['- ' + line.product_id.display_name for line in lines_without_route]),
                     '\n'.join(['- ' + line.product_id.display_name for line in lines_without_route])))
        
        res = super().action_confirm()
        
        # Create and post invoice automatically after confirmation
        for order in self:
            if order.state == 'sale':  # Only create invoice if order is confirmed
                invoice = order._create_invoices()
                if invoice:
                    # Post the invoice immediately
                    invoice.action_post()
                    
                    # # Show warning message
                    # return {
                    #     'name': _('การแจ้งเตือน'),
                    #     'type': 'ir.actions.act_window',
                    #     'res_model': 'warning.message.wizard',
                    #     'view_mode': 'form',
                    #     'target': 'new',
                    #     'context': {
                    #         'default_message': _('ใบแจ้งหนี้ได้ถูกสร้างขึ้นแล้ว กรุณาตรวจสอบข้อมูลการชำระเงินและทำการลงทะเบียนการชำระเงิน\n - หากไม่มียอดเรียกเก็บปลายทาง กรุณาลงทะเบียนการชำระเงินทันที\n - หากเป็นการเก็บเงินปลายทาง(COD) ไม่ต้องทำการบันทึกการชำระเงิน\n - หากเป็น Platform กรุณาทำการยืนยันการชำระเงินทันที')
                    #     }
                    # }
                    
        return res 