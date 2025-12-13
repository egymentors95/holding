{
    "name": "Editable Sale Order Lines in Odoo 25 Inventory",
    "version": "1.0",
    "summary": "Allows editing of sale order lines in Odoo 25 Inventory module",
    "description": """
        This module extends the Odoo 25 Inventory functionality to allow users to edit sale order lines
        directly from the inventory interface. It enhances user experience by providing flexibility in managing
        sale orders without navigating away from the inventory module.
    """,
    "author": "Custom Project Holding",
    "website": "https://www.customprojectholding.com",
    "category": "Inventory",
    "depends": [
        "sale",
        "sale_management",
        "sale_margin",
        "account",
        "odex25_account_asset",
        "mrp",
        "ksa_zatca_integration",
    ],
    "data": [
        "security/groups_views.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "views/account_move_views.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}