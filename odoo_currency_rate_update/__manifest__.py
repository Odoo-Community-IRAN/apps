# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Odoo Currency Rate Update",
    "summary": """Update currency rates from live sources""",
    "description": """Update currency rates from live sources""",
    "author": "Odoo Community Iran",
    "website": "https://odoo-community.ir/",
    "category": "Accounting/Accounting",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "account", "currency_rate_live"],
    "data": [
        "security/ir.model.access.csv",
        "data/transaction_type_data.xml",
        "views/res_company.xml",
    ],
    "installable": True,
}
