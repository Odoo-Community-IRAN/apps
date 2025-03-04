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
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["payment"],
    "data": [
        "views/payment_views.xml",
        "views/payment_zarinpal_templates.xml",
        "data/payment_provider_zarinpal.xml",
    ],
    "external_dependencies": {
        "python": ["suds"],
    },
    "installable": True,
    "application": True,
}
