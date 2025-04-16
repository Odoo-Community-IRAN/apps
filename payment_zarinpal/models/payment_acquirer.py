# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import json
import requests

SUPPORTED_CURRENCIES = ('IRR', 'IRT')

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('zarinpal', 'zarinpal')],
        ondelete={'zarinpal': 'set default'}
    )
    zarinpal_merchant_id = fields.Char(
        string="zarinpal Merchant ID",
        help="The ID solely used to identify the account with zarinpal",
        required_if_provider='zarinpal'
    )
    zarinpal_account_id = fields.Char(
        string="zarinpal Account ID",
        help="The ID solely used to identify the country-dependent shop with zarinpal",
        required_if_provider='zarinpal'
    )
    zarinpal_api_key = fields.Char(
        string="zarinpal API Key", required_if_provider='zarinpal',
        groups='base.group_system'
    )

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist zarinpal providers for unsupported currencies. """
        providers = super()._get_compatible_providers(
            *args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in SUPPORTED_CURRENCIES:
            providers = providers.filtered(lambda a: a.code != 'zarinpal')

        return providers

    def _zarinpal_generate_sign(self, values, incoming=True):
        """ Generate the signature for incoming or outgoing communications.

        :param dict values: The values used to generate the signature
        :param bool incoming: Whether the signature must be generated for an incoming (zarinpal to
                              Odoo) or outgoing (Odoo to zarinpal) communication.
        :return: The signature
        :rtype: str
        """

        ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
        req_data = {
            "merchant_id": values['merchantId'],
            "amount": values['amount'],  # IRR
            "callback_url": values['apiBackUrl'],
            "description": values['description'],
            "metadata": {}
        }

        if values['buyerMobile']:
            req_data['metadata']['mobile'] = values['buyerMobile']
        if values['buyerEmail']:
            req_data['metadata']['email'] = values['buyerEmail']

        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            authority = req.json()['data']['authority']
            return authority
        else:
            raise ValidationError(
                req.json()['errors']['message'] + ' [ ' + str(req.json()['errors']['code']) + ' ]')

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'zarinpal':
            return super()._get_default_payment_method_codes()
        return ['zarinpal']
