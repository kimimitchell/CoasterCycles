# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_ids = fields.Many2many(
        'stock.picking', string='Inventory Transfers',
        copy=False, states={'done': [('readonly', True)]},
        domain="[('state', '=', 'done'), ('id', 'in', available_picking_ids)]" )
    available_picking_ids = fields.Many2many('stock.picking', compute="_compute_picking_ids", )
    inventory_compare_line_ids = fields.One2many('inventory.compare.line', 'move_id', string='Invetory Compare Lines')
    inventory_values_applied = fields.Boolean(string='Have The Inventory Valuation Values Been Applied', default=False)
    has_inventory_compare_lines = fields.Boolean(string='Move Has Inventory Compare Lines', default=False, compute="_compute_has_inventory_compare_lines")

    @api.depends('invoice_origin')
    def _compute_picking_ids(self):
        for record in self:
            record.available_picking_ids = self.env['stock.picking'].search([('origin', '=', record.invoice_origin)])

    @api.depends('inventory_compare_line_ids')
    def _compute_has_inventory_compare_lines(self):
        for record in self:
            if len(record.inventory_compare_line_ids):
                record.has_inventory_compare_lines = True
            else:
                record.has_inventory_compare_lines = False

    def action_compute_inventory_compare_lines(self):
        for line in self.invoice_line_ids:
            transfer_unit_price = line.purchase_line_id.price_unit
            if transfer_unit_price != line.price_unit:
                vals = {
                    'quantity': line.quantity,
                    'product_id': line.product_id.id, 
                    'bill_unit_price': line.price_unit,
                    'transfer_unit_price': transfer_unit_price,
                    'move_id': line.move_id.id,
                    'currency_id': line.currency_id.id
                }
                target_line = self.inventory_compare_line_ids.filtered(lambda l: l.product_id == line.product_id)
                if target_line:
                    target_line.update(vals)
                else:
                    self.env['inventory.compare.line'].create(vals)

    def action_apply_inventory_values(self):
        self.ensure_one()
        landed_costs_lines = self.inventory_compare_line_ids.filtered(lambda line: line.difference_unit_price != 0)
        extra_cost_product = self.env['product.template'].search([('id', '=', 1914)], limit=1)

        landed_costs = self.env['stock.landed.cost'].create({
            'vendor_bill_id': self.id,
            'cost_lines': [(0, 0, {
                'product_id': extra_cost_product.id,
                'name': extra_cost_product.name,
                'account_id': extra_cost_product.get_product_accounts()['stock_input'].id,
                'price_unit': l.difference_unit_price * l.quantity,
                'split_method': l.product_id.split_method_landed_cost or 'equal',
            }) for l in landed_costs_lines],
            'picking_ids': self.picking_ids,
        })

        for lc in landed_costs:
            lc.compute_landed_cost()
        self.inventory_values_applied = True
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])
