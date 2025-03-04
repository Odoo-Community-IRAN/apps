# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from kavenegar import KavenegarAPI, HTTPException, APIException
from odoo import api, fields, models
from .sms_api import KAVENEGAR_SMS_STATUS_CODE


class KavenegarSmsProvider(models.Model):
    _name = "kavenegar.sms.provider"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    api_key = fields.Char(required=True)
    sender_number = fields.Char(required=True)
    credit = fields.Float(readonly=True)
    latest_credit_update = fields.Datetime(readonly=True)
    sequence = fields.Integer()

    @api.model
    def cron_update_sms_status(self):
        sms_to_update = self.env["sms.sms"].search([
            ("state", "=", "pending"),
            ("messageid", "!=", False),
            ("write_date", ">", datetime.now() - timedelta(days=1)),
            ("write_date", "<", datetime.now() - timedelta(minutes=5))
        ])
        if sms_to_update:
            self = self.search([], order="sequence asc", limit=1)
            messageids = ",".join(sms_to_update.mapped("messageid"))
            params = {"messageid" : messageids}
            try:
                kn_api = KavenegarAPI(self.api_key)
                response = kn_api.sms_status(params)

                for entry in response:
                    sms_record = self.env["sms.sms"].search([
                        ("messageid", "=", entry["messageid"]), 
                        ("to_delete", "=", False)
                    ])
                    sms_status = KAVENEGAR_SMS_STATUS_CODE.get(entry["status"], "error")
                    vals = {"state": sms_status}
                    if sms_status in ["sent", "canceled"]:
                        vals["to_delete"] = True
                    elif sms_status == "error":
                        vals["failure_type"] = "sms_server"
                    sms_record.write(vals)
            except (APIException, HTTPException) as e:
                self.message_post(body=e.args[0], subject="Exception")

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
