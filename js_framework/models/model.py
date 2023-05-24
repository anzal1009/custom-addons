from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Dashboard(models.Model):
    _name = 'account.dashboard'

    name = fields.Char(string="Name")