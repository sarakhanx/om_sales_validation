from odoo import models, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
                    
                    # แก้ไขข้อความแจ้งเตือนของการยืนยันคำสั่งขาย
                    return {
                        'name': _('การแจ้งเตือน'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'warning.message.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_message': _('ใบแจ้งหนี้ได้ถูกสร้างขึ้นแล้ว กรุณาตรวจสอบข้อมูลการชำระเงินและทำการลงทะเบียนการชำระเงิน\n - หากไม่มียอดเรียกเก็บปลายทาง กรุณาลงทะเบียนการชำระเงินทันที\n - หากเป็นการเก็บเงินปลายทาง(COD) ไม่ต้องทำการบันทึกการชำระเงิน\n - หากเป็น Platform กรุณาทำการยืนยันการชำระเงินทันที')
                        }
                    }
                    
        return res 