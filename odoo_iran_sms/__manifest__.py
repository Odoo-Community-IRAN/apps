# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Odoo Iran SMS",
    "summary": """SMS sending with Kavenegar for Iran""",
    "description": """
Odoo Iran SMS - Kavenegar Integration
=====================================

This module integrates Kavenegar SMS service with Odoo's SMS functionality.

Features:
    * Send SMS using Kavenegar API
    * Support for Iranian phone numbers
    * SMS status tracking and updates
    * Credit monitoring
    * Multi-company support
    * Automatic phone number formatting for Iran

Configuration:
    * Configure your Kavenegar API key and sender number
    * The module will automatically use Kavenegar for SMS sending
    """,
    "category": "Hidden/Tools",
    "version": "19.0.1.0.0",
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
    "auto_install": False,
}
