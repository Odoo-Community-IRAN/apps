# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Odoo Iran SMS",
    "summary": """SMS sending with Kavenegar""",
    "description": """This module handles sms sending, using Kavenegar provider""",
    "category": "Hidden/Tools",
    "version": "17.0.1.0.0",
    "author": "Odoo Community Iran",
    "website": "https://odoo-community.ir",
    "license": "AGPL-3",
    "depends": ["base", "sms"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/kavenegar_sms_provider.xml",
        "views/res_config_setting.xml",
    ],
    "external_dependencies": {
        "python": ["kavenegar"],
    },
    "installable": True,
}
