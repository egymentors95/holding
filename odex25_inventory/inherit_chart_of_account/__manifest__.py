{
    "name": "Saudi Arabia - Customize L10n_sa",
    "version": "1.0",
    "summary": "Customization for l10n_sa",
    "description": """
        This module provides customizations for the Saudi Arabia localization (l10n_sa) in O
        Odoo. It includes enhancements to the account move model to support specific requirements
        such as QR code generation and confirmation date handling.
    """,
    "author": "AitecSoft",
    "website": "",
    "category": "Accounting",
    "depends": ['account'],
    "data": [
        "views/account_account_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}