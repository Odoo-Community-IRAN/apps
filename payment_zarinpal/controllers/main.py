# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
import pprint

_logger = logging.getLogger(__name__)


class PaymentZarinpalController(http.Controller):
    _return_url = '/payment/zarinpal/return/<string:uuid>'
    _webhook_url = '/payment/zarinpal/webhook'

    @http.route(_return_url, type='http', auth='public',
                methods=['GET'], save_session=False)
    def zarinpal_return(self, **data):
        request.env['payment.transaction'].sudo(
        )._handle_notification_data('zarinpal', data)
        return request.redirect('/payment/status')

    @http.route(_webhook_url, type='http', auth='public',
                methods=['POST'], csrf=False)
    def zarinpal_webhook(self, **data):
        state_pol = data.get('state_pol')
        if state_pol == '4':
            lapTransactionState = 'APPROVED'
        elif state_pol == '6':
            lapTransactionState = 'DECLINED'
        elif state_pol == '5':
            lapTransactionState = 'EXPIRED'
        else:
            lapTransactionState = f'INVALID state_pol {state_pol}'

        data = {
            'signature': data.get('sign'),
            'TX_VALUE': data.get('value'),
            'currency': data.get('currency'),
            'referenceCode': data.get('reference_sale'),
            'transactionId': data.get('transaction_id'),
            'transactionState': data.get('state_pol'),
            'message': data.get('response_message_pol'),
            'lapTransactionState': lapTransactionState,
        }

        try:
            request.env['payment.transaction'].sudo(
            )._handle_notification_data('zarinpal', data)
        except ValidationError:
            _logger.warning(
                'zarinpal ************** An error occurred while handling the confirmation from PayU with data:\n%s',
                pprint.pformat(data))
        return http.Response(status=200)
