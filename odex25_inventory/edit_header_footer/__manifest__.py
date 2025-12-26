{
    'name': 'Custom Report Header',
    'version': '14.0.1.0',
    'depends': ['base', 'web', 'l10n_gcc_invoice', 'account'],
    'author': 'IBS',
    'website': 'http://www.ibs.com',
    'license': 'AGPL-3',
    'summary': 'Customize report header and footer',
    'description': """
        This module allows customization of the report header and footer.
        You can modify the company details, add logos, and change the layout of the header and footer sections in reports.
    """,
    'data': [
        'views/account_move_view.xml',
        'views/res_company_views.xml',
        'views/report_templates.xml',
        'views/invoice_report_views.xml',
        'views/inherit_report_invoice.xml',

    ],
    'installable': True,
    'application': False,
}
