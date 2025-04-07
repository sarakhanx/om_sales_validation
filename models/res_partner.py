from odoo import models, fields, api
import re
import json
import os

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
            if partner.city:
                address_parts.append(partner.city)
            if partner.state_id:
                address_parts.append(partner.state_id.name)
            if partner.zip:
                address_parts.append(partner.zip)
            if partner.country_id:
                address_parts.append(partner.country_id.name)
            partner.full_address = ', '.join(address_parts)

    def _load_mappings(self):
        """Load province and country mappings from JSON file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, '..', 'data', 'thai_provinces.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('provinces', {}), data.get('countries', {})
        except Exception as e:
            return {}, {}

    @api.onchange('full_address')
    def _inverse_full_address(self):
        for partner in self:
            if not partner.full_address:
                continue

            # Store original address for street field
            original_address = partner.full_address

            # Remove phone numbers in parentheses and duplicate phone numbers
            address = partner.full_address
            # Remove phone numbers in parentheses
            address = re.sub(r'\([^)]*โทร[^)]*\)', '', address)
            # Remove duplicate phone numbers
            address = re.sub(r'\([^)]*\)', '', address)
            # Remove phone numbers with country code
            address = re.sub(r'\(\+[0-9]+\)[0-9]+', '', address)
            # Remove standalone phone numbers
            address = re.sub(r'[0-9]{9,10}', '', address)
            # Clean up multiple spaces and commas
            address = re.sub(r'\s+', ' ', address)
            address = re.sub(r',\s*,', ',', address)
            address = address.strip(' ,')

            # Extract ZIP code (5 digits)
            zip_match = re.search(r'(\d{5})', address)
            if zip_match:
                partner.zip = zip_match.group(1)
                address = address.replace(zip_match.group(1), '').strip(' ,')

            # Extract state and city
            state_city_match = re.search(r'([^,]+),([^,]+),([^,]+),([^,]+)$', address)
            if state_city_match:
                street = state_city_match.group(1).strip()
                city = state_city_match.group(2).strip()
                state = state_city_match.group(3).strip()
                country = state_city_match.group(4).strip()

                # Set street - use original address for street field
                if street:
                    partner.street = original_address

                # Set city
                if city:
                    partner.city = city

                # Set state with Thai-English mapping
                if state:
                    # Load mappings from JSON
                    province_mapping, _ = self._load_mappings()
                    
                    # Try to find province in mapping
                    english_state = province_mapping.get(state)
                    if english_state:
                        state_id = self.env['res.country.state'].search([
                            ('name', 'ilike', english_state),
                            ('country_id', '=', partner.country_id.id)
                        ], limit=1)
                    else:
                        # If not found in mapping, try direct search
                        state_id = self.env['res.country.state'].search([
                            ('name', 'ilike', state),
                            ('country_id', '=', partner.country_id.id)
                        ], limit=1)
                    
                    if state_id:
                        partner.state_id = state_id.id

                # Set country with name variations
                if country:
                    # Load mappings from JSON
                    _, country_mapping = self._load_mappings()
                    
                    # Map country name variations
                    normalized_country = country_mapping.get(country.lower(), country)
                    
                    # Search for country with multiple conditions
                    country_id = self.env['res.country'].search([
                        '|',
                        ('name', 'ilike', normalized_country),
                        ('code', 'ilike', normalized_country)
                    ], limit=1)
                    
                    if country_id:
                        partner.country_id = country_id.id 