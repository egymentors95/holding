{
    "name": "Taxes Reports",
    "version": "1.0",
    "summary": "Custom Taxes Reports for Odex25 Inventory",
    "description": """
        This module provides custom tax reports tailored for the Odex25 Inventory system.
    """,
    "author": "El-Araby",
    "category": "Accounting",
    "depends": ["account", 'base', 'expense_product_report'],
    "data": [
        "security/ir.model.access.csv",
        # "views/account_tax_views.xml",
        # "views/description_note_views.xml",
        "wizard/tax_report_wizard.xml",
        "wizard/total_tax_report.xml",
        "reports/action_reports.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}