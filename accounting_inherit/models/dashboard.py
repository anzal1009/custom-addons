from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Dashboard(models.Model):
    _name = 'dashboard'

    name = fields.Char(string="Name")


    def dashboard_action(self):
        if self.name == "Sales Invoice":
            action = self.env.ref('sale.action_sale_order_form_view').read()[0]
            return action


        if self.name == "Quotations/Proforma":
            action = self.env.ref('sale.action_orders').read()[0]
            action['domain'] = [('state', '=', "draft")]
            return action

        if self.name == "AMC Details":
            action = self.env.ref('accounting_inherit.action_view_amc').read()[0]
            return action

        if self.name == "Profit and Loss":
            action = self.env.ref('sales_profit_loss_report.action_sales_profit_report_wizard').read()[0]
            return action





