# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['zarinpal'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    @api.model
    def _get_sdd_payment_method_code(self):
        res = super()._get_sdd_payment_method_code()
        res.append('zarinpal')
        return res
