{
    "name": "View Location Warehouse by Users",
    "version": "1.0",
    "author": "IBS",
    "category": "Warehouse",
    "description": """
    This module adds a new menu item to the Warehouse Management menu, which allows users to view the location of a warehouse by users.
    """,
    "depends": [
        "base",
        "stock",
    ],
    "data": [
        "views/res_users.xml",
        "views/stock_location.xml",
        "views/stock_warehouse.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "LGPL-3",
}

