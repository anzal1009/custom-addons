from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Templates(models.Model):
    _name = 'templates'

    template_name = fields.Selection([("proposal", "Proposal Letter"), ("experience", "Experience Certicate"), ("offer", "Offer Letter"), ("cover", "Cover Page"), ("slip", "Salary Slip")], string="Choose Template")
    date = fields.Date(string="Date")
    client_name = fields.Many2one('res.partner', string="Client Name")
    client = fields.Many2one('res.partner', string="Client Name")
    name = fields.Char(string="Recipient Name")
    address = fields.Char(string="Address")
    rec_name = fields.Char(string="Recipient Name")
    company = fields.Many2one('res.company', string="Our Company")
    starting_date = fields.Date(string="Starting Period")
    start_date = fields.Date(string="Starting Period")
    employ_date = fields.Date(string="Starting Period")
    ending_date = fields.Date(string="Ending Period")
    end_date = fields.Date(string="Ending Period")
    project = fields.Char(string="Project Name")
    cost = fields.Integer(string="Cost")
    designation = fields.Char(string="Designation")
    salary = fields.Integer(string="Salary")
    product = fields.Char(string="Product")
    post = fields.Char(string="Post of")








