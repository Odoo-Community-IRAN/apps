# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Odoo Iran Print",
    "summary": """Odoo Iran Print""",
    "description": """Odoo Iran Print""",
    "category": "Accounting/Localizations/Reporting",
    "version": "1.0.0",
    "author": "Odoo Community Iran",
    "website": "https://odoo-community.ir",
    "license": "AGPL-3",
    "depends": ["base", "account_reports", "sale"],
    "data": [
        "report/paper_formats.xml",
        "report/external_layout_sale.xml",
        "report/sale_report.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "l10n_ir_account_reports/static/src/scss/web_report.scss",
            "l10n_ir_account_reports/static/src/scss/fonts.scss",
            "l10n_ir_account_reports/static/src/scss/report.scss",
            "l10n_ir_account_reports/static/src/css/pdf_style.css",
        ],
    },
    "installable": True,
}
