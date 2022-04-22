# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InventoryCompareLine(models.Model):
    _name = 'inventory.compare.line'
    _description = 'Inventory Compare Lines'

    quantity = fields.Float(string='quantity')
    product_id = fields.Many2one('product.product', string='Product')
    bill_unit_price = fields.Float(string='Bill Unit Price')
    transfer_unit_price = fields.Float(string='Transfer Unit Price')
    difference_unit_price = fields.Float(string='Difference Unit Price', compute='_compute_difference_unit_price')
    move_id = fields.Many2one('account.move', string='Account Move')
    picking_ids = fields.Many2many('stock.picking', string='Inventory Transfers', compute='_compute_picking_ids')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.depends('bill_unit_price', 'transfer_unit_price')
    def _compute_difference_unit_price(self):
        for record in self:
            record.difference_unit_price = record.bill_unit_price - record.transfer_unit_price
    
    @api.model_create_single
    def create(self, vals):
        for record in self:
            record.quantity = vals['quantity']
            record.product_id = vals['product_id']
            record.bill_unit_price = vals['bill_unit_price']
            record.transfer_unit_price = vals['transfer_unit_price']
            record.move_id = vals['move_id']
            record.currency_id = vals['currency_id']
        return super(InventoryCompareLine, self).create(vals)
    
    def update(self, vals):
        for record in self:
            record.quantity = vals['quantity']
            record.bill_unit_price = vals['bill_unit_price']
            record.transfer_unit_price = vals['transfer_unit_price']
            record.move_id = vals['move_id']
            record.currency_id = vals['currency_id']
        return record

    @api.depends('move_id')
    def _compute_picking_ids(self):
        for record in self:
            record.picking_ids = record.move_id.picking_ids