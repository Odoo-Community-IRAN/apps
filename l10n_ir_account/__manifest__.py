# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Iran - Accounting",
    "version": "1.0.1",
    "countries": ["ir"],
    "category": "Accounting/Localizations/Account Charts",
    "summary": """iran accounting chart and localization.""",
    "description": """iran accounting chart and localization.""",
    "license": "AGPL-3",
    "website": "https://odoo-community.ir",
    "depends": ["account"],
    "data": [
        "data/res_currency_data.xml",
        "data/res.bank.csv",
    ],
}
