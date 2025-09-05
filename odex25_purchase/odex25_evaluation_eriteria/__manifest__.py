# -*- coding: utf-8 -*-
{
    'name': "Evaluation Eriteria",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','purchase_requisition_custom'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'wizard/intial_evaluation_wizard.xml',
        'wizard/final_evaluation_wizard.xml',
        'reports/initial_evaluation_view.xml',
        'reports/initial_evaluation_report.xml',
        'reports/final_evaluation_view.xml',
        'reports/final_evaluation_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
