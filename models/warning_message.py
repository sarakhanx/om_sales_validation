from odoo import models, fields

class WarningMessageWizard(models.TransientModel):
    _name = 'warning.message.wizard'
    _description = 'Warning Message Wizard'

    message = fields.Text('Message', required=True) 