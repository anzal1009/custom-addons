from odoo import models, fields, api

class AccountJournal(models.Model):

    _inherit = 'account.move'


    sign = fields.Boolean("Apply Signature")