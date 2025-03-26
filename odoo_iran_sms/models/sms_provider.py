# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from kavenegar import KavenegarAPI, HTTPException, APIException
from odoo import fields, models


class KavenegarSmsProvider(models.Model):
    _name = "kavenegar.sms.provider"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    api_key = fields.Char(required=True)
    sender_number = fields.Char(required=True)
    credit = fields.Float(readonly=True)
    latest_credit_update = fields.Datetime(readonly=True)
    sequence = fields.Integer()

    def action_credit_btn(self):
        self.ensure_one()
        try:
            kn_api = KavenegarAPI(self.api_key)
            response = kn_api.account_info()
            self.credit = response["remaincredit"]
            self.latest_credit_update = datetime.now()
        except (APIException, HTTPException) as e:
            self.message_post(body=e.args[0], subject="Exception")


class SmsSms(models.Model):
    _inherit = "sms.sms"

    messageid = fields.Char(readonly=True)

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        try:
            result = super(SmsSms, self)._send(
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
                raise_exception=raise_exception,
            )
            return result
        except Exception:
            return True
