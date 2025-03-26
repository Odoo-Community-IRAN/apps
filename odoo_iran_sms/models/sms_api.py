# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.sms.tools.sms_api import SmsApi
from kavenegar import KavenegarAPI

KAVENEGAR_SMS_STATUS_CODE = {
    1: "pending",
    2: "pending",
    4: "pending",
    5: "pending",
    6: "error",
    10: "sent",
    11: "error",
    13: "canceled",
    14: "error",
    100: "error",
}


class SmsApiInherit():
    def _contact_iap(self, local_endpoint, params, timeout=15):
        params["dbuuid"] = self.env["ir.config_parameter"].sudo().get_param("database.uuid")
        res = SmsApiInherit.send_sms(self, params)
        return res

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
        recipient_numbers = [number["number"] for number in messages[0]["numbers"]]
        recipient_uuids = [number["uuid"] for number in messages[0]["numbers"]]
        sms_records = self.env["sms.sms"].search([
            ("uuid", "in", recipient_uuids),
            ("to_delete", "=", False),
        ])
        sms_records.write({"state": "process"})

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
                ("to_delete", "=", False)
            ])
            sms_status = KAVENEGAR_SMS_STATUS_CODE.get(entry["status"], "error")
            vals = {"messageid": entry["messageid"], "state": sms_status}

            if sms_status in ["sent", "canceled"]:
                vals["to_delete"] = True
            elif sms_status == "error":
                vals["failure_type"] = "sms_server"

            sms_record.write(vals)

        return response


SmsApi._send_sms_batch = SmsApiInherit._send_sms_batch
SmsApi._contact_iap = SmsApiInherit._contact_iap
