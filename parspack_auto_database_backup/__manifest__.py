# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Parspack Auto Database Backup",
    "summary": """Parspack Auto Database Backup""",
    "version": "1.0.0",
    "category": "Extra Tools",
    "description": "This module has been developed for creating database "
                   "backups automatically and store it to the different "
                   "locations",
    "author": "Odoo Community Iran",
    "website": "https://odoo-community.ir/",
    "depends": ["base", "mail", "auto_database_backup"],
    "data": [
        "views/db_backup_configure_views.xml",
    ],
    "external_dependencies": {
        "python": ["boto3"]
    },
    "license": "LGPL-3",
}
