// Copyright (C) 2024-Today: Odoo Community Iran
// @author: Odoo Community Iran (https://odoo-community.ir/
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { loadBundle, loadJS } from "@web/core/assets";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";



patch(WebClient.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            if(luxon.DateTime.now().locale == 'fa-IR'){
                await loadBundle("persian_calendar.calendar_persian");
            }
        });
    }
})