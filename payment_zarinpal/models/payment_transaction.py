# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_zarinpal.controllers.main import PaymentZarinpalController
from werkzeug import urls
import json
import logging
import requests
import uuid

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    zarinpal_signature = fields.Char(string="signature")
    zarinpal_uuid = fields.Char(string="uuid")

    @api.model
    def _compute_reference(self, provider, prefix=None, separator='-', **kwargs):
        """ Override of payment to ensure that zarinpal requirements for references are satisfied.

        zarinpal requirements for transaction are as follows:
        - References must be unique at provider level for a given merchant account.
          This is satisfied by singularizing the prefix with the current datetime. If two
          transactions are created simultaneously, `_compute_reference` ensures the uniqueness of
          references by suffixing a sequence number.

        :param str provider: The provider of the acquirer handling the transaction
        :param str prefix: The custom prefix used to compute the full reference
        :param str separator: The custom separator used to separate the prefix from the suffix
        :return: The unique reference for the transaction
        :rtype: str
        """
        if provider == 'zarinpal':
            if not prefix:
                # If no prefix is provided, it could mean that a module has passed a kwarg intended
                # for the `_compute_reference_prefix` method, as it is only called if the prefix is
                # empty. We call it manually here because singularizing the prefix would generate a
                # default value if it was empty, hence preventing the method from ever being called
                # and the transaction from received a reference named after the related document.
                prefix = self.sudo()._compute_reference_prefix(
                    provider, separator, **kwargs
                ) or None
            prefix = payment_utils.singularize_reference_prefix(prefix=prefix, separator=separator)
        return super()._compute_reference(provider, prefix=prefix, separator=separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return zarinpal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_id.code != 'zarinpal':
            return res
        website = self.env['website'].get_current_website()
        if not website:
            raise ValidationError('plz , set domain name first')

        base_url = self.get_base_url()

        randomCode = uuid.uuid4()
        apiBackUrl = urls.url_join(base_url,'/payment/zarinpal/return/'+str(randomCode)+'/')
        ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"

        zarinpal_values = {
            'merchantId': self.provider_id.zarinpal_merchant_id,
            'referenceCode': self.reference,
            'description': self.reference,
            'amount': int(processing_values['amount'])*10 if self.currency_id.name =="IRT" else int(processing_values['amount']),
            'tax': 0,
            'taxReturnBase': 0,
            'currency': self.currency_id.name,
            'accountId': self.provider_id.zarinpal_account_id,
            'buyerFullName': self.partner_name,
            'buyerEmail': self.partner_email,
            'buyerMobile': self.partner_id.mobile,
            'responseUrl': urls.url_join(base_url, PaymentZarinpalController._return_url),
            'confirmationUrl': urls.url_join(base_url, PaymentZarinpalController._webhook_url),
            'api_url': ZP_API_STARTPAY,
            'randomCode': randomCode,
            'apiBackUrl': apiBackUrl,
        }
        zarinpal_values['signature'] = self.provider_id._zarinpal_generate_sign(
            zarinpal_values, incoming=False
        )
        self.write({
                'zarinpal_signature':zarinpal_values['signature'],
                'zarinpal_uuid':zarinpal_values['randomCode'],
                'state':'draft'
                })
        zarinpal_values['api_url'] = ZP_API_STARTPAY + zarinpal_values['signature']
        return zarinpal_values

    @api.model
    def _get_tx_from_notification_data(self, provider, data):
        """ Override of payment to find the transaction based on zarinpal data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        :raise: ValidationError if the signature can not be verified
        """
        tx = super()._get_tx_from_notification_data(provider, data)
        if provider != 'zarinpal':
            return tx

        zarinpal_signature = data.get('Authority')
        zarinpal_uuid = data.get('uuid')
        tx = self.search([('zarinpal_signature', '=', zarinpal_signature),('zarinpal_uuid', '=', zarinpal_uuid), ('provider_id.code', '=', 'zarinpal')])

        if not tx:
            raise ValidationError(
                "Zarinpal: " + _("No transaction found matching reference.")
            )

        if data.get('Status') != 'OK':
            state = 'cancel'
            state_message =  _("Transaction failed or canceled by user")
        else:
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req_data = {
                "merchant_id": tx.provider_id.zarinpal_merchant_id,
                "amount": int(tx.amount)*10 if tx.currency_id.name =="IRT" else int(tx.amount),  
                "authority": zarinpal_signature
            }
            ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100 :
                    state = 'done'
                    state_message = _("Transaction success.\nRefID: " + str(req.json()['data']['ref_id']))
                elif t_status == 101:
                    state = 'done'
                    state_message = _("Transaction submitted : " + str(req.json()['data']['message']))
                else:
                    state = 'error'
                    state_message = _("Transaction failed.\nStatus: " + str(req.json()['data']['message']))
            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                state = 'error'
                state_message = _(f"Error code: {e_code}, Error Message: {e_message}")
        tx.write({
            'state':state,
            'state_message':state_message
        })
        return tx

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on zarinpal data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        """
        # super(PaymentTransaction, self)._process_feedback_data(data)
        super()._process_notification_data(data)

        self.ensure_one()
        if self.provider_id.code != 'zarinpal':
            return

        # self.acquirer_reference = data.get('transactionId')
        #
        status = self.state
        state_message = self.state_message
        if status == 'done':
            self._set_done(state_message=state_message)
        elif status in ('error','cancel'):
            self._set_canceled(state_message=state_message)
        else:
            _logger.warning(
                "received unrecognized payment state %s for transaction with reference %s",
                status, self.reference
            )
            self._set_error("zarinpal: " + _("Invalid payment status.") + '[%s]'%status)