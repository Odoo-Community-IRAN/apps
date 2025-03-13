# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Iran - Accounting",
    "summary": """Iran accounting chart and localization.""",
    'author': "Odoo Community Iran",
    'website': "https://odoo-community.ir/",
    "category": "Accounting/Localizations/Account Charts",
    "version": "1.0.0",
    "license": "AGPL-3",
    "countries": ["ir"],
    "depends": ["account"],
    "data": [
        "data/res_currency_data.xml",
        "data/res.bank.csv",
    ],
}
