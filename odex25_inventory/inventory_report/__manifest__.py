{
    "name": "Inventory Product Report",
    "version": "14.0.0.1.0",
    "category": "Product",
    "summary": "Inventory Product Report",
    "author": "IBS",
    "website": "https://www.ibs-na.com",
    "license": "AGPL-3",
    "depends": ['base', 'stock', 'report_xlsx', 'account', 'purchase_requisition_custom', 'partner_category'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/inventory_wizard_views.xml",
        "views/stock_views.xml",
        "views/product_template_views.xml",

        "reports/inventory_report_template_views.xml",
        "reports/action_reports.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
