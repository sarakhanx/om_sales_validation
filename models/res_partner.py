from odoo import models, fields, api
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'

    full_address = fields.Text(
        string='Full Address Block',
        help='Paste the complete address here to auto-fill the fields below',
        compute='_compute_full_address',
        inverse='_inverse_full_address',
    )

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _compute_full_address(self):
        for partner in self:
            address_parts = []
            if partner.street:
                address_parts.append(partner.street)
            if partner.street2:
                address_parts.append(partner.street2)
            if partner.city and partner.state_id:
                address_parts.append(f"{partner.city}, {partner.state_id.code}")
            if partner.zip:
                address_parts.append(partner.zip)
            if partner.country_id:
                address_parts.append(partner.country_id.name)
            partner.full_address = '\n'.join(address_parts)

    def _inverse_full_address(self):
        for partner in self:
            if not partner.full_address:
                continue

            # แยกที่อยู่เป็นบรรทัด
            lines = partner.full_address.strip().split('\n')
            
            for line in lines:
                # ค้นหารหัสไปรษณีย์
                zip_match = re.search(r'\d{5}', line)
                if zip_match:
                    partner.zip = zip_match.group()
                    
                    # แยกส่วนต่างๆ ของที่อยู่
                    # Format: บ้านเลขที่/ถนน แขวง/ตำบล เขต/อำเภอ จังหวัด รหัสไปรษณีย์
                    parts = line[:zip_match.start()].strip().split(' ')
                    
                    # หาตำแหน่งของคำว่า "แขวง" "เขต" "จังหวัด" หรือ "กรุงเทพมหานคร"
                    district_idx = -1
                    amphur_idx = -1
                    province_idx = -1
                    
                    for i, part in enumerate(parts):
                        if any(word in part for word in ['แขวง', 'ตำบล']):
                            district_idx = i
                        elif any(word in part for word in ['เขต', 'อำเภอ']):
                            amphur_idx = i
                        elif 'จังหวัด' in part or part == 'กรุงเทพมหานคร':
                            province_idx = i
                    
                    # แยกที่อยู่
                    if district_idx > 0:
                        partner.street = ' '.join(parts[:district_idx])
                        if amphur_idx > district_idx:
                            partner.street2 = ' '.join(parts[district_idx:amphur_idx])
                    else:
                        partner.street = ' '.join(parts[:amphur_idx]) if amphur_idx > 0 else ' '.join(parts)
                    
                    # กำหนดจังหวัด
                    if province_idx > 0:
                        province = parts[province_idx]
                        partner.city = province
                        
                        # ถ้าเป็นกรุงเทพฯ
                        if province == 'กรุงเทพมหานคร':
                            state = self.env['res.country.state'].search([
                                ('code', '=', 'BK')
                            ], limit=1)
                            if state:
                                partner.state_id = state.id
                    
                    # ถ้าไม่มีการระบุจังหวัดชัดเจน ใช้ส่วนสุดท้ายก่อนรหัสไปรษณีย์
                    elif amphur_idx > 0:
                        partner.city = ' '.join(parts[amphur_idx:])
                    
                    # ตั้งค่าประเทศเป็นไทย
                    thailand = self.env['res.country'].search([
                        ('code', '=', 'TH')
                    ], limit=1)
                    if thailand:
                        partner.country_id = thailand.id
                    break  # ออกจากลูปเมื่อพบที่อยู่ที่มีรหัสไปรษณีย์ 