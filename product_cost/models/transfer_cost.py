from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo import exceptions


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move'

    transfer_unit_cost = fields.Float(string="Product Unit Cost", default=0.0)


class ConsolidatedSv:
    def __init__(self, product_id, unit_cost, value, account_mids, sv):
        self.product_id = product_id
        self.unit_cost = unit_cost
        self.value = value
        self.account_mids = [account_mids]
        self.sv = [sv]


class ConsolidatedLots:
    def __init__(self, move_id, product_id, product_name, lot, lot_qty, lot_purchase_rate, value, qty):
        self.move_id = move_id
        self.product_id = product_id
        self.product_name = product_name
        self.lots = [lot]
        self.lot_qty = [lot_qty]
        self.lot_purchase_rate = [lot_purchase_rate]
        self.value = value
        self.qty = qty


class StockMoveCustomTransferCost(models.Model):
    _inherit = 'stock.picking'

    custom_transfer_cost_status = fields.Boolean(string="Custom Cost Status", default=False, readonly =True)

    def CustomTransferCost(self):
        if self.picking_type_id.code == 'outgoing': #Only for sale(outgoing_transfer)
            items_consolidated = {}
            cost_not_found = []
            for line in self.move_ids_without_package:
                print("hiii",line.id)
                if line.quantity_done > 0:
                    item_found = False
                    for line2 in line.move_line_ids:
                        item_found = True
                        if line2.qty_done > 0:
                            lot_found = False
                            purchase_moves = self.env['stock.move'].sudo().search(
                                [('product_id', '=', line.product_id.id), ('purchase_line_id', '!=', False), ('company_id', '=', self.company_id.id)], order='id DESC') or False

                            if purchase_moves:
                                for purchase_move in purchase_moves:
                                    stock_line = self.env['stock.move.line'].sudo().search(
                                        [('move_id', '=', purchase_move.id), ('lot_id', '=', line2.lot_id.id), ('company_id', '=', self.company_id.id)]) or False

                                    if (stock_line):
                                        if purchase_move.purchase_line_id.price_unit > 0:
                                            lot_found = True
                                            if line.id in items_consolidated.keys():
                                                cons_sv = items_consolidated[line.id]
                                                cons_sv.qty += line2.qty_done
                                                cons_sv.value += line2.qty_done * purchase_move.purchase_line_id.price_unit
                                                cons_sv.lots.append(
                                                    line2.lot_id.name)
                                                cons_sv.lot_qty.append(
                                                    line2.qty_done)
                                                cons_sv.lot_purchase_rate.append(
                                                    purchase_move.purchase_line_id.price_unit)
                                                line.transfer_unit_cost = cons_sv.value/cons_sv.qty

                                            else:
                                                items_consolidated[line.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name, line2.qty_done,
                                                                                            purchase_move.purchase_line_id.price_unit, line2.qty_done * purchase_move.purchase_line_id.price_unit, line2.qty_done)
                                                line.transfer_unit_cost = purchase_move.purchase_line_id.price_unit
                                            break

                            # if not purchase
                            if not lot_found:
                                prod_moves = self.env['stock.move'].sudo().search(
                                    [('product_id', '=', line.product_id.id), ('production_id', '!=', False),
                                    ('company_id', '=', self.company_id.id)], order='id DESC') or False
                                # if production
                                if prod_moves:
                                    for prod_move in prod_moves:
                                        move_prod_lines = self.env['stock.move.line'].sudo().search(
                                            [('move_id', '=', prod_move.id), ('lot_id', '=', line2.lot_id.id),
                                            ('company_id', '=', self.company_id.id)]) or False

                                        if move_prod_lines:
                                            value = self.env['stock.valuation.layer'].sudo().search(
                                                [('stock_move_id', '=', prod_move.id),
                                                ('company_id', '=', self.company_id.id)]) or False

                                            if value:
                                                if value.unit_cost > 0:
                                                    lot_found = True
                                                    if line.id in items_consolidated.keys():
                                                        cons_sv = items_consolidated[line.id]
                                                        cons_sv.qty += line2.qty_done
                                                        cons_sv.value += line2.qty_done * value.unit_cost
                                                        cons_sv.lots.append(
                                                            line2.lot_id.name)
                                                        cons_sv.lot_qty.append(
                                                            line2.qty_done)
                                                        cons_sv.lot_purchase_rate.append(
                                                            value.unit_cost)
                                                        line.transfer_unit_cost = cons_sv.value / cons_sv.qty
                                                    else:
                                                        items_consolidated[line.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name,
                                                                                                    line2.qty_done, value.unit_cost,
                                                                                                    line2.qty_done * value.unit_cost,
                                                                                                    line2.qty_done)
                                                        line.transfer_unit_cost = value.unit_cost
                                                    break

                            if not lot_found:
                                cost_not_found.append({
                                    'product_name': line.product_id.name,
                                    'lot': line2.lot_id.name})
                                if line.product_id.id in items_consolidated.keys():
                                    cons_sv = items_consolidated[line.product_id.id]
                                    cons_sv.qty += line2.qty_done
                                    cons_sv.value += 0
                                    cons_sv.lots.append(line2.lot_id.name)
                                    cons_sv.lot_qty.append(line2.qty_done)
                                    cons_sv.lot_purchase_rate.append(0)
                                else:
                                    items_consolidated[line.product_id.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name,
                                                                                            line2.qty_done, 0,
                                                                                            0,
                                                                                            line2.qty_done)

                    if not item_found:
                        cost_not_found.append(
                            {'product_name': line.product_id.name, 'lot': 'not found'})
                        if line.product_id.id in items_consolidated.keys():
                            # sv_found = True
                            cons_sv = items_consolidated[line.product_id.id]
                            cons_sv.qty += line.quantity_done
                            cons_sv.value += 0
                            cons_sv.lots.append('not found')
                            cons_sv.lot_qty.append(0)
                            cons_sv.lot_purchase_rate.append(0)
                        else:
                            items_consolidated[line.product_id.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, 'not found',
                                                                                    0, 0,
                                                                                    0,
                                                                                    line.quantity_done)

            # Add rate to stock stock_valuation and create corresponding journal Sale.
                transferNumber = self.name
                transferData = self.env['stock.picking'].sudo().search(
                    [('name', '=', transferNumber), ('state', '=', "done")])
                if transferData:

                    print(transferData.name)
                    print(line.product_id.name)
                    print(line.transfer_unit_cost)


                    transferData.note = "test"
                    itemName = line.product_id.name
                    itemRate = float(line.transfer_unit_cost)
                    itemId = itemName and self.env['product.product'].sudo().search(
                        [('name', '=', itemName)], limit=1) or False
                    stockValuation = self.env['stock.valuation.layer'].sudo().search(
                        [('description', 'like', transferNumber), ('product_id', '=', itemId.id),('stock_move_id','=',line.id)])
                    if stockValuation:
                        for stockValuationLine in stockValuation:
                            itemTotal = float(stockValuationLine.quantity) * float(itemRate)
                            stockValuationLine.unit_cost = itemRate
                            stockValuationLine.value = itemTotal


                            print(stockValuationLine.unit_cost)
                            print(stockValuationLine.value)

                            journals = self.env['account.move'].sudo().search(
                                [('id', '=', stockValuationLine.account_move_id.id)])
                            for journal in journals:
                                journal.button_draft()
                                journal.name = False
                                journal.unlink()

                            journal_ref = transferNumber + " - " + itemName
                            journal_account = self.env['account.journal'].sudo().search(
                                [('name', '=', "Inventory Valuation"), ('company_id', '=', stockValuationLine.company_id.id)], limit=1) or False

                            journal_entry = self.env['account.move'].sudo().create({
                                'move_type': "entry",
                                'ref': journal_ref,
                                'date': stockValuationLine.create_date,
                                'journal_id': journal_account.id,
                                'company_id': stockValuationLine.company_id.id,
                                'partner_id': self.partner_id.id,
                                'line_ids': [(0, 0, {
                                    'name': journal_ref,
                                    'debit': float(itemTotal * -1),
                                    'partner_id': self.partner_id.id,
                                    'account_id': itemId.categ_id.property_stock_account_output_categ_id.id
                                }), (0, 0, {
                                    'name': journal_ref,
                                    'credit': float(itemTotal * -1),
                                    'partner_id': self.partner_id.id,
                                    'account_id': itemId.categ_id.property_stock_valuation_account_id.id

                                })]
                            })

                            for j_entry in journal_entry:
                                j_entry.sudo().action_post()

                            stockValuation.account_move_id = journal_entry
        self.custom_transfer_cost_status = True








# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, UserError
# from odoo import exceptions
#
#
# class StockMoveLineInherit(models.Model):
#     _inherit = 'stock.move'
#
#     transfer_unit_cost = fields.Float(string="Product Unit Cost", default=0.0)
#
#
# class ConsolidatedSv:
#     def __init__(self, product_id, unit_cost, value, account_mids, sv):
#         self.product_id = product_id
#         self.unit_cost = unit_cost
#         self.value = value
#         self.account_mids = [account_mids]
#         self.sv = [sv]
#
#
# class ConsolidatedLots:
#     def __init__(self, move_id, product_id, product_name, lot, lot_qty, lot_purchase_rate, value, qty):
#         self.move_id = move_id
#         self.product_id = product_id
#         self.product_name = product_name
#         self.lots = [lot]
#         self.lot_qty = [lot_qty]
#         self.lot_purchase_rate = [lot_purchase_rate]
#         self.value = value
#         self.qty = qty
#
#
# class StockMoveCustomTransferCost(models.Model):
#     _inherit = 'stock.picking'
#
#     custom_transfer_cost_status = fields.Boolean(string="Custom Cost Status", default=False, readonly =True)
#
#     def CustomTransferCost(self):
#         if self.picking_type_id.code == 'outgoing': #Only for sale(outgoing_transfer)
#             items_consolidated = {}
#             cost_not_found = []
#             for line in self.move_ids_without_package:
#                 if line.quantity_done > 0:
#                     item_found = False
#                     for line2 in line.move_line_ids:
#                         item_found = True
#                         if line2.qty_done > 0:
#                             lot_found = False
#                             purchase_moves = self.env['stock.move'].sudo().search(
#                                 [('product_id', '=', line.product_id.id), ('purchase_line_id', '!=', False), ('company_id', '=', self.company_id.id)], order='id DESC') or False
#
#                             if purchase_moves:
#                                 for purchase_move in purchase_moves:
#                                     stock_line = self.env['stock.move.line'].sudo().search(
#                                         [('move_id', '=', purchase_move.id), ('lot_id', '=', line2.lot_id.id), ('company_id', '=', self.company_id.id)]) or False
#
#                                     if (stock_line):
#                                         if purchase_move.purchase_line_id.price_unit > 0:
#                                             lot_found = True
#                                             if line.id in items_consolidated.keys():
#                                                 cons_sv = items_consolidated[line.id]
#                                                 cons_sv.qty += line2.qty_done
#                                                 cons_sv.value += line2.qty_done * purchase_move.purchase_line_id.price_unit
#                                                 cons_sv.lots.append(
#                                                     line2.lot_id.name)
#                                                 cons_sv.lot_qty.append(
#                                                     line2.qty_done)
#                                                 cons_sv.lot_purchase_rate.append(
#                                                     purchase_move.purchase_line_id.price_unit)
#                                                 line.transfer_unit_cost = cons_sv.value/cons_sv.qty
#
#                                             else:
#                                                 items_consolidated[line.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name, line2.qty_done,
#                                                                                             purchase_move.purchase_line_id.price_unit, line2.qty_done * purchase_move.purchase_line_id.price_unit, line2.qty_done)
#                                                 line.transfer_unit_cost = purchase_move.purchase_line_id.price_unit
#                                             break
#
#                             # if not purchase
#                             if not lot_found:
#                                 prod_moves = self.env['stock.move'].sudo().search(
#                                     [('product_id', '=', line.product_id.id), ('production_id', '!=', False),
#                                     ('company_id', '=', self.company_id.id)], order='id DESC') or False
#                                 # if production
#                                 if prod_moves:
#                                     for prod_move in prod_moves:
#                                         move_prod_lines = self.env['stock.move.line'].sudo().search(
#                                             [('move_id', '=', prod_move.id), ('lot_id', '=', line2.lot_id.id),
#                                             ('company_id', '=', self.company_id.id)]) or False
#
#                                         if move_prod_lines:
#                                             value = self.env['stock.valuation.layer'].sudo().search(
#                                                 [('stock_move_id', '=', prod_move.id),
#                                                 ('company_id', '=', self.company_id.id)]) or False
#
#                                             if value:
#                                                 if value.unit_cost > 0:
#                                                     lot_found = True
#                                                     if line.id in items_consolidated.keys():
#                                                         cons_sv = items_consolidated[line.id]
#                                                         cons_sv.qty += line2.qty_done
#                                                         cons_sv.value += line2.qty_done * value.unit_cost
#                                                         cons_sv.lots.append(
#                                                             line2.lot_id.name)
#                                                         cons_sv.lot_qty.append(
#                                                             line2.qty_done)
#                                                         cons_sv.lot_purchase_rate.append(
#                                                             value.unit_cost)
#                                                         line.transfer_unit_cost = cons_sv.value / cons_sv.qty
#                                                     else:
#                                                         items_consolidated[line.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name,
#                                                                                                     line2.qty_done, value.unit_cost,
#                                                                                                     line2.qty_done * value.unit_cost,
#                                                                                                     line2.qty_done)
#                                                         line.transfer_unit_cost = value.unit_cost
#                                                     break
#
#                             if not lot_found:
#                                 cost_not_found.append({
#                                     'product_name': line.product_id.name,
#                                     'lot': line2.lot_id.name})
#                                 if line.product_id.id in items_consolidated.keys():
#                                     cons_sv = items_consolidated[line.product_id.id]
#                                     cons_sv.qty += line2.qty_done
#                                     cons_sv.value += 0
#                                     cons_sv.lots.append(line2.lot_id.name)
#                                     cons_sv.lot_qty.append(line2.qty_done)
#                                     cons_sv.lot_purchase_rate.append(0)
#                                 else:
#                                     items_consolidated[line.product_id.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, line2.lot_id.name,
#                                                                                             line2.qty_done, 0,
#                                                                                             0,
#                                                                                             line2.qty_done)
#
#                     if not item_found:
#                         cost_not_found.append(
#                             {'product_name': line.product_id.name, 'lot': 'not found'})
#                         if line.product_id.id in items_consolidated.keys():
#                             # sv_found = True
#                             cons_sv = items_consolidated[line.product_id.id]
#                             cons_sv.qty += line.quantity_done
#                             cons_sv.value += 0
#                             cons_sv.lots.append('not found')
#                             cons_sv.lot_qty.append(0)
#                             cons_sv.lot_purchase_rate.append(0)
#                         else:
#                             items_consolidated[line.product_id.id] = ConsolidatedLots(line.id, line.product_id.id, line.product_id.name, 'not found',
#                                                                                     0, 0,
#                                                                                     0,
#                                                                                     line.quantity_done)
#
#             # Add rate to stock stock_valuation and create corresponding journal Sale.
#                 transferNumber = self.name
#                 transferData = self.env['stock.picking'].sudo().search(
#                     [('name', '=', transferNumber), ('state', '=', "done")])
#
#                 print("rate",line.transfer_unit_cost)
#                 if transferData:
#                     transferData.note = "test"
#                     itemName = line.product_id.name
#                     itemRate = float(line.transfer_unit_cost)
#                     itemId = itemName and self.env['product.product'].sudo().search(
#                         [('name', '=', itemName)], limit=1) or False
#                     stockValuation = self.env['stock.valuation.layer'].sudo().search(
#                         [('description', 'like', transferNumber), ('product_id', '=', itemId.id)], limit=1)
#                     if stockValuation:
#                         for stockValuationLine in stockValuation:
#                             itemTotal = float(stockValuationLine.quantity) * float(itemRate)
#                             stockValuationLine.unit_cost = itemRate
#                             stockValuationLine.value = itemTotal
#
#                             journals = self.env['account.move'].sudo().search(
#                                 [('id', '=', stockValuation.account_move_id.id)])
#                             for journal in journals:
#                                 journal.button_draft()
#                                 journal.name = False
#                                 journal.unlink()
#
#                             journal_ref = transferNumber + " - " + itemName
#                             journal_account = self.env['account.journal'].sudo().search(
#                                 [('name', '=', "Inventory Valuation"), ('company_id', '=', stockValuationLine.company_id.id)], limit=1) or False
#
#                             journal_entry = self.env['account.move'].sudo().create({
#                                 'move_type': "entry",
#                                 'ref': journal_ref,
#                                 'date': stockValuation.create_date,
#                                 'journal_id': journal_account.id,
#                                 'company_id': stockValuationLine.company_id.id,
#                                 'partner_id': self.partner_id.id,
#                                 'line_ids': [(0, 0, {
#                                     'name': journal_ref,
#                                     'debit': float(itemTotal * -1),
#                                     'partner_id': self.partner_id.id,
#                                     'account_id': itemId.categ_id.property_stock_account_output_categ_id.id
#                                 }), (0, 0, {
#                                     'name': journal_ref,
#                                     'credit': float(itemTotal * -1),
#                                     'partner_id': self.partner_id.id,
#                                     'account_id': itemId.categ_id.property_stock_valuation_account_id.id
#
#                                 })]
#                             })
#
#                             for j_entry in journal_entry:
#                                 j_entry.sudo().action_post()
#
#                             stockValuation.account_move_id = journal_entry
#             self.custom_transfer_cost_status = True
