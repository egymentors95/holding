{
    'name': 'Custom Report Header',
    'version': '14.0.1.0',
    'depends': ['base', 'web', 'l10n_gcc_invoice'],
    'data': [
        'views/res_company_views.xml',
        'views/report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
