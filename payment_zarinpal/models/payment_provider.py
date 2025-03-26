# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from suds.client import Client

ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl' 


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[
        ('zarinpal', 'Zarinpal')
    ], ondelete={'zarinpal': 'set default'})

    zarinpal_merchant_id= fields.Char(string="Zarinpal Merchant id", required_if_provider='zarinpal', groups='base.group_user')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist ZarinPal acquirers when the currency is not supported. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in ['IRR']:
            acquirers = acquirers.filtered(lambda a: a.provider != 'zarinpal')

        return acquirers

    def _zarinpal_get_api_url(self):
        """ Return the API URL according to the acquirer state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()
        if self.state == 'enabled':
            return {
                'zarinpal_start_pay': 'https://www.zarinpal.com/pg/StartPay/', # Authority
                'zarinpal_request': 'https://api.zarinpal.com/pg/v4/payment/request.json',
                'zarinpal_verify': 'https://api.zarinpal.com/pg/v4/payment/verify.json', 
            }
        else:
            return {
                'zarinpal_start_pay': 'https://sandbox.zarinpal.com/pg/StartPay/', # Authority
                'zarinpal_request': 'https://sandbox.zarinpal.com/pg/v4/payment/request.json',
                'zarinpal_verify': 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json', 
            }


    def _zarinpal_generate_signature(self, values):
        """ Generate the signature for incoming or outgoing communications.

        :param dict values: The values used to generate the signature
        :return: The signature
        :rtype: str
        """
        client = Client(ZARINPAL_WEBSERVICE) # raise URLError(err)
        result= client.service.PaymentRequest(self.zarinpal_merchant_id,
                    values['amount'],
                    values['description'],
                    values['email'], # partner_email
                    values['phone'], # partner_phone
                    values['callback_url'])
        print(values['callback_url'])
        if result.Status == 100:
            return result.Authority
        return ''


    def _get_default_payment_method_id(self, code):
        self.ensure_one()
        if self.provider != 'zarinpal':
            return super()._get_default_payment_method_id(code)
        return self.env.ref('payment_zarinpal.payment_method_zarinpal').id