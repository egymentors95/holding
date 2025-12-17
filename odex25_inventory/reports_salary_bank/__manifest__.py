{
    "name": "Reports Salary Bank",
    "version": "14.0.0.1.0",
    "category": "Hr",
    "summary": "Reports Salary Bank",
    "author": "El-Araby",
    "website": "",
    "license": "AGPL-3",
    "depends": ['base','report_xlsx','account', 'exp_hr_payroll', 'hr_contract_custom', 'hr_base'],
    "data": [
        "security/ir.model.access.csv",
        "reports/total_payslip_report.xml",
        "views/total_payslip_views.xml",
        "wizard/salary_bank_wizard_views.xml",
        "wizard/total_salary_bank_views.xml",
        "reports/template_views.xml",
        "reports/action_reports.xml",

    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}