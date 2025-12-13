{
    "name": "Access Partner",
    "version": "14.0.0.1.0",
    "category": "All",
    "summary": "Access Partner for all modules",
    "author": "Elaraby",
    "website": "https://www.ibs-na.com",
    "license": "AGPL-3",
    "depends": ['base','account', 'sale', 'purchase', 'contacts', 'stock', 'mrp'],
    "data": [
        "security/security_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_viwes.xml",
        # "views/contact_views.xml",
        # "views/products_views.xml",
    ],
    "installable": True,

    "application": False,
    "auto_install": False,
}
