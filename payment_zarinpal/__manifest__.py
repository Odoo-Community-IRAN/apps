# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Zarinpal Payment Acquirer",
    "summary": "Payment Acquirer: zarinpal Implementation",
    "description": """zarinpal payment acquirer""",
    "author": "Odoo Community Iran",
    "website": "https://odoo-community.ir/",
    "category": "Accounting/Payment Acquirers",
    "version": "1.0.1",
    "license": "AGPL-3",
    "depends": ["base", "account", "payment"],
    "data": [
        "views/payment_views.xml",
        "views/payment_zarinpal_templates.xml",
        "data/payment_acquirer_data.xml",
    ],
    "installable": True,
    "application": True,
    'uninstall_hook': 'uninstall_hook',
}
