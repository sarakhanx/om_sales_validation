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
        
        return super().action_confirm() 