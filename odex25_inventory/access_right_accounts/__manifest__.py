{
    "name": "Report Account Move",
    "version": "14.0.0.1.0",
    "summary": "Customizations for Account Move Reports",
    "description": "This module provides customizations for account move reports in Odoo.",
    "category": "Accounting",
    "author": "Aitecsoft",
    "website": "https://www.aitecsoft.com",
    "license": "AGPL-3",
    "depends": ["account", "hr_expense", "product_margin", "product", "base", 'account_budget_custom', 'odex25_account_reports'],
    "data": [
        "security/security_views.xml",
        "security/ir.model.access.csv",
        "views/menuitem_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,

}