{
    "name": "Sales Partner Report",
    "version": "14.0.0.1.0",
    "category": "Product",
    "summary": "Sales Partner Report",
    "author": "IBS",
    "website": "https://www.ibs-na.com",
    "license": "AGPL-3",
    "depends": ['base','stock', 'report_xlsx','account', 'partner_category', 'product_report'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sales_report_wizard_views.xml",
        "reports/report_template_views.xml",
        "reports/action_reports.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}