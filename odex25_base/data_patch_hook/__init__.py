from odoo import api, SUPERUSER_ID
from odoo.exceptions import ValidationError


def post_init_hook(cr, registry):
    """
    This function serves as the hook to apply data patches and commit changes
    before raising an intentional error.
    """
    # Example functions to call (define these functions elsewhere in this file)
    update_due_date_in_transaction_model(cr, registry)

    # Commit the changes
    cr.commit()

    # Raise an intentional error to prevent module installation
    raise ValidationError("Intentional error: This module is not designed to be installed.\nData Applied Successfully!")

def update_due_date_in_transaction_model(cr, registry):
    """
    Recalculate the is_late field for all records after module upgrade.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    transaction_models = ['outgoing.transaction', 'internal.transaction', 'incoming.transaction']
    for transaction_model in transaction_models:
        model = env[transaction_model]
        records = model.search([])  # Fetch all records
        records.compute_due_date()  # Trigger computation