{
    "name": "Partner Category",
    "version": "14.0.0.1.0",
    "category": "Contact",
    "summary": "Partner Category",
    "author": "IBS",
    "website": "https://www.ibs-na.com",
    "license": "AGPL-3",
    "depends": ['base','stock', 'report_xlsx','account', 'product'],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/product_template_views.xml",
        "views/product_category_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}