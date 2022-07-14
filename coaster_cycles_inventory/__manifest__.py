# -*- coding: utf-8 -*-
{
    "name": "Coaster Cycles: Inventory Development",
    "summary": """Inventory Valuation Based On Invoiced Price""",
    "description": """
        Task: 2667713

    """,
    "author": "Odoo Inc",
    "license": "OEEL-1",
    "website": "http://www.odoo.com",
    "category": "Custom Development",
    "version": "0.1",
    "depends": ['stock_landed_costs', 'sale_stock', 'sale', 'account_accountant', 'stock_account'],
    "data": [
        'views/view_move_form_inherit.xml',
        'security/ir.model.access.csv'
    ]
}