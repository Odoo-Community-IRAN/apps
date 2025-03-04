# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_zarinpal.controllers.main import ZarinpalController
from suds.client import Client
from werkzeug import urls

ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl' 


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    zarinpal_refid = fields.Char(
        string='zarinpal Reference Id',
        readonly=True,
        help='Reference of the TX as stored in the acquirer database'
    )
    zarinpal_authority = fields.Char(
        string='zarinpal authority',
        readonly=True,
        help='Reference of the TX as stored in the acquirer database'
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Paypal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'zarinpal':
            return res
        base_url = self.provider_id.get_base_url()

        zarinpal_values =  {
            'amount': self.amount,
            'merchant_id': self.provider_id.zarinpal_merchant_id,
            'callback_url': urls.url_join(base_url, ZarinpalController._callback_url),
            'description': "name:" + self.partner_name + "amount:" + str(self.amount) + "reference:" + self.reference,
            'email': self.partner_email or "no@yahoo.com",
            'phone': self.partner_email or "+98",
        }

        zarinpal_values['Authority'] = self.provider_id._zarinpal_generate_signature(zarinpal_values)
        zarinpal_values['api_url'] = self.provider_id._zarinpal_get_api_url()['zarinpal_start_pay'] + zarinpal_values['Authority']

        tx = self.search([('reference', '=', self.reference)])
        tx.zarinpal_authority = zarinpal_values['Authority']
        tx.zarinpal_refid = self.reference
        return zarinpal_values

    @api.model
    # TODO RM  _get_tx_from_notification_data
    def _get_tx_from_notification_data(self, provider, data):
        """ Override of payment to find the transaction based on Paypal data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider, data)
        if provider != 'zarinpal':
            return tx

        authority = data.get('Authority')
        tx = self.search([('zarinpal_authority', '=', authority), ('provider_code', '=', 'zarinpal')])
        if not tx:
            raise ValidationError(
                "ZarinPal: " + _("No transaction found matching reference %s.", tx.reference)
            )

        return tx
    # TODO _process_notification_data
    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Paypal data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        try:
            super()._process_notification_data(notification_data) # TODO FIX error 
        except Exception as e:
            print(str(e))
            # Expected singleton: payment.transaction()

        if self.provider_code != 'zarinpal':
            return

        status = notification_data.get('Status')
        authority = notification_data.get('Authority')

        tx = self.search([('zarinpal_authority', '=', authority), ('provider_code', '=', 'zarinpal')])
        if status == 'OK':
            tx_result = self.zarinpal_verify_request(authority)
            if tx_result.Status == 100:
                tx.zarinpal_refid = tx_result.RefID
                self._set_done()
            elif tx_result.Status == 101:
                self._set_done()
            else:
                self._set_error(
                    "Zarinpal: " + _("The payment encountered an error with code %s", tx_result.Status)
                )
        elif status == 'NOK':
            self._set_error(
                "Zarinpal: " + _("The payment encountered an error with code %s", status)
            )
        else : 
            self._set_error(
                "Zarinpal: " + _("The payment encountered an error with code %s", 'Unknown Error')
            )

    def zarinpal_verify_request(self, data):
        client = Client(ZARINPAL_WEBSERVICE)
        result = client.service.PaymentVerification(
            self.provider_id.zarinpal_merchant_id,
            data,
            self.amount
        )
        return result
