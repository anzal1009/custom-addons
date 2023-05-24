from odoo import models, fields, api

class AccountJournal(models.Model):

    _inherit = 'account.move'


    sign = fields.Boolean("Apply Signature")
    rating = fields.Selection([
        ('0', 'Worst'),
        ('1', 'Poor'),
        ('2', 'Bad'),
        ('3', 'Average'),('4', 'Above Avg'),('5', 'Out Standing')], string="Rating")

