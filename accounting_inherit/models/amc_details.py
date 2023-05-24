from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AmcDetails(models.Model):
    _name = 'amc.details'

    client_name = fields.Many2one('res.partner', string="Client Name")
    project = fields.Char(string="Project Name")

    street = fields.Char('Street', readonly=False, store=True)
    street2 = fields.Char('Street2', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, readonly=False, store=True)
    city = fields.Char('City', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)
    #

    starting_date = fields.Date(string="Starting Period")
    ending_date = fields.Date(string="Ending Period")
    payment = fields.Selection([("bank", "Bank"), ("cash", "Cash")], string="Payment Mode")
    modifications = fields.Char(string="Modifications")
    payment_terms = fields.Many2one('account.payment.term', string="Payment Terms")

    amc_line_ids = fields.One2many('amc.details.lines', 'client_name', tracking=True,
                                   string="Amc Lines")
    total = fields.Float(string="Total Amount", compute='_compute_sum', digits=0)

    @api.depends('amc_line_ids.bill')
    def _compute_sum(self):
        for rec in self:
            total = 0
            for line in rec.amc_line_ids:
                total += line.amount
            rec.total = total


class AmcDetailsLines(models.Model):
    _name = "amc.details.lines"
    _description = "Amc Details Lines"

    date = fields.Date(string="Date")
    bill = fields.Many2one('account.move', string="Bill")
    amount = fields.Integer(string="Amount")
    # customer = fields.Many2one('res.partner', string="Customer")
    client_name = fields.Many2one('amc.details', tracking=True, string="Client Name")

    # total_qty_nos = fields.Float(string="Total Ordered Nos" ,compute='_compute_nos_quantity', digits=0)
    # total_qty_lit = fields.Float(string="Total Ordered Liter" ,compute='_compute_lit_quantity', digits=0)
    # total_qty_units = fields.Float(string="Total Ordered Units" ,compute='_compute_unit_quantity', digits=0)
    # total_qty_lit = fields.Float(string="Total Ordered Liter" ,compute='_compute_lit_quantity', digits=0)
    # t_qty = fields.Char("qty" ,compute='_compute_sum_quantity')

    #

    @api.onchange('bill')
    def _onchange_bill(self):
        for rec in self:
            print(rec)
            search = self.env['account.move'].search([('id', '=', rec.bill.id)])
            if search:
                rec.amount = search.amount_total
                rec.date = search.invoice_date
                # rec.customer = search.partner_id
            else:
                pass
            # lines = [(5, 0, 0)]
            # for line in self.bill.amc_line_ids:
            #     vals = {
            #         'date': line.invoice_date,
            #         'amount': line.amount_total
            #     }
            #
            #     lines.append((0, 0, vals))
            # rec.amc_line_ids = lines
