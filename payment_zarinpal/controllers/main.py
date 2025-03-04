# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import http
from odoo.http import request
import pprint
import logging

_logger = logging.getLogger(__name__)


class ZarinpalController(http.Controller):
    _callback_url = '/payment/zarinpal/verify'

    @http.route([_callback_url], type='http', auth='public', methods=['GET'], csrf=False, save_session=False,website=True)
    def zarinpal_callback(self, **get):
        _logger.info('received ZarinPal return data %s', pprint.pformat(get))
        if get:
            request.env['payment.transaction'].sudo()._handle_notification_data('zarinpal', get)

        return request.redirect('/payment/status')
