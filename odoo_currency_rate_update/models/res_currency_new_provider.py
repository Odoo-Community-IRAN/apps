# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from .currency_fetcher import CurrencyFetcher
import datetime


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection(
        selection_add=[('tgju', 'TGJU Provider')],
    )

    @api.model
    def create(self, vals):
        transaction_type = 'purchase'  # default
        transaction_type_id = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_currency_rate_update.transaction_type_id', default=False
        )

        if transaction_type_id:
            default_transaction_type = self.env['transaction.type.config'].browse(int(transaction_type_id))
            if default_transaction_type:
                transaction_type = default_transaction_type.transaction_type

        vals['transaction_type'] = transaction_type

        return super(ResCompany, self).create(vals)

    @api.model
    def init(self):
        super(ResCompany, self).init()
        for company in self:
            transaction_type = 'purchase'  # default
            transaction_type_id = self.env['ir.config_parameter'].sudo().get_param(
                'odoo_currency_rate_update.transaction_type_id', default=False
            )

            if transaction_type_id:
                default_transaction_type = self.env['transaction.type.config'].browse(int(transaction_type_id))
                if default_transaction_type:
                    transaction_type = default_transaction_type.transaction_type

            company.transaction_type = transaction_type

    def _parse_tgju_data(self, available_currencies):
        cf = CurrencyFetcher()
        transaction_type = 'purchase'  # default
        transaction_type_id = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_currency_rate_update.transaction_type_id', default=False
        )

        if transaction_type_id:
            default_transaction_type = self.env['transaction.type.config'].browse(int(transaction_type_id))
            if default_transaction_type:
                transaction_type = default_transaction_type.transaction_type

        data = cf.get_currency_data('USD', transaction_type)

        currency_rates = {
            'USD': data.get('dollar_price'),
        }

        rates_dict = {}
        date_rate = datetime.date.today()
        available_currency_codes = [currency.name for currency in available_currencies]

        for currency_code, rate in currency_rates.items():
            if currency_code in available_currency_codes:
                rates_dict[currency_code] = (float(1.0 / rate), date_rate)

        if 'IRR' in available_currency_codes:
            rates_dict['IRR'] = (1, date_rate)

        return rates_dict
