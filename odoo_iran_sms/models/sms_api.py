# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from kavenegar import KavenegarAPI
from odoo import api, models

KAVENEGAR_SMS_STATUS_CODE = {
    1: "sent",
    2: "sent",
    4: "sent",
    5: "sent",
    6: "error",
    10: "sent",
    11: "error",
    13: "canceled",
    14: "error",
    100: "error",
}


class SmsApiInherit(models.AbstractModel):
    _inherit = "sms.api"

    @api.model
    def _contact_iap(self, local_endpoint, params, timeout=15):
        params["dbuuid"] = self.env["ir.config_parameter"].sudo().get_param("database.uuid")
        res = self.send_sms(params)
        return res

    @api.model
    def _send_sms_batch(self, messages, delivery_reports_url=False):
        return self._contact_iap("/iap/sms/3/send", {
            "messages": messages,
            "webhook_url": delivery_reports_url,
        })

    def send_sms(self, params):
        sms_provider = self.env["kavenegar.sms.provider"].search([], order="sequence asc", limit=1)

        if not params.get("messages") or not sms_provider:
            return {"error": "No messages or provider found"}

        messages = params["messages"]
        message_content = messages[0]["content"]
        recipient_numbers = [message["number"] for message in messages]

        kn_api = KavenegarAPI(sms_provider.api_key)
        params = {
            "sender": sms_provider.sender_number,
            "receptor": ",".join(recipient_numbers),
            "message": message_content,
        }
        response = kn_api.sms_send(params)

        for entry in response:
            num_with_country_code = "+98" + entry["receptor"][1:]
            sms_record = self.env['sms.sms'].search([
                ("number", "in", [num_with_country_code, entry["receptor"]]),
            ])
            sms_status = KAVENEGAR_SMS_STATUS_CODE.get(entry["status"], "error")
            vals = {"messageid": entry["messageid"], "state": sms_status}

            if sms_status == "error":
                vals["failure_type"] = "sms_server"

            sms_record.write(vals)

        return response
