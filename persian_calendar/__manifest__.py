# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Persian Calendar",
    'summary': """Persian Calendar""",
    'description': """Persian Calendar""",
    'author': "Odoo Community Iran",
    'website': "https://odoo-community.ir/",
    'category': 'Localization/Iran',
    'version': '1.0.3',
    'license': 'LGPL-3',
    'depends': ['base', 'web',],
    'assets': {
        'web.assets_backend': [
            'persian_calendar/static/lib/jalali/utils.js',
            'persian_calendar/static/src/js/persian-date.js',
            'persian_calendar/static/src/js/farvardin.js',
            'persian_calendar/static/src/js/datepicker/datetimepicker_service.js',
            'persian_calendar/static/src/js/loader.js',
        ],
        'persian_calendar.calendar_persian':[
            'persian_calendar/static/src/js/format_utils.js',
            'persian_calendar/static/src/js/list.js',
            'persian_calendar/static/src/js/datepicker/datetime_field.js',
            'persian_calendar/static/src/js/datepicker/datetime_picker.js',
            'persian_calendar/static/src/js/jdatetime.js',
            'persian_calendar/static/src/js/kanban.js',
        ]
    }
}
