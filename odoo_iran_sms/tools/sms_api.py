# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.sms.tools.sms_api import SmsApiBase
from kavenegar import KavenegarAPI, HTTPException, APIException
import logging

_logger = logging.getLogger(__name__)

# Corrected Kavenegar SMS Status Mapping
KAVENEGAR_SMS_STATUS_CODE = {
    1: "process",        # در صف ارسال
    2: "process",        # زمان‌بندی شده
    4: "process",        # در حال ارسال
    5: "sent",           # ارسال به مخابرات ← FIXED: This should be "sent"
    6: "server_error",   # خطا در ارسال
    10: "sent",          # رسیده به گیرنده
    11: "server_error",  # نرسیده به گیرنده
    13: "canceled",      # لغو شده
    14: "server_error",  # بلاک شده (فیلتر شده)
    100: "server_error", # خطای نامشخص
}

# Kavenegar error code to failure type mapping
KAVENEGAR_ERROR_TO_FAILURE_TYPE = {
    6: "sms_server",     # خطا در ارسال
    11: "sms_server",    # نرسیده به گیرنده
    14: "sms_server",    # بلاک شده
    100: "unknown",      # خطای نامشخص
}


class SmsApiKavenegar(SmsApiBase):
    """Kavenegar SMS API implementation for Odoo 19"""
    
    PROVIDER_TO_SMS_FAILURE_TYPE = SmsApiBase.PROVIDER_TO_SMS_FAILURE_TYPE | {
        'kavenegar_error': 'sms_server',
        'invalid_api_key': 'sms_acc',
        'insufficient_credit': 'sms_credit',
        'kavenegar_blocked': 'sms_server',
    }

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        """Send SMS batch using Kavenegar API
        
        :param list messages: list of SMS messages to send
        :param str delivery_reports_url: webhook URL for delivery reports (not used)
        :return: list of results with uuid and state
        """
        # Get company and provider
        company_sudo = (self.company or self.env.company).sudo()
        sms_provider = self.env["kavenegar.sms.provider"].search([
            '|',
            ('company_ids', '=', False),
            ('company_ids', 'in', company_sudo.id),
            ('active', '=', True)
        ], order="sequence asc", limit=1)
        
        if not sms_provider:
            _logger.error("No Kavenegar SMS provider configured for company %s", company_sudo.name)
            return [{'uuid': msg_data['numbers'][0]['uuid'], 'state': 'server_error'} 
                   for msg in messages for msg_data in [msg]]
        
        results = []
        
        for message in messages:
            content = message['content']
            numbers_data = message['numbers']
            
            # Extract phone numbers and UUIDs
            recipient_numbers = [num_data['number'] for num_data in numbers_data]
            recipient_uuids = [num_data['uuid'] for num_data in numbers_data]
            
            try:
                # Initialize Kavenegar API
                kn_api = KavenegarAPI(sms_provider.api_key)
                
                # Prepare parameters for Kavenegar
                params = {
                    "sender": sms_provider.sender_number,
                    "receptor": ",".join(self._clean_phone_numbers(recipient_numbers)),
                    "message": content,
                }
                
                _logger.info("Sending SMS via Kavenegar API to %s recipients", len(recipient_numbers))
                
                # Send SMS via Kavenegar
                response = kn_api.sms_send(params)
                
                _logger.info("Kavenegar API response: %s", response)
                
                # Process response
                for i, entry in enumerate(response):
                    if i < len(recipient_uuids):
                        # Map Kavenegar status to Odoo status
                        kavenegar_status = entry.get("status", 100)
                        odoo_state = KAVENEGAR_SMS_STATUS_CODE.get(kavenegar_status, "server_error")
                        
                        _logger.info("SMS UUID %s: Kavenegar status %s -> Odoo state %s", 
                                   recipient_uuids[i], kavenegar_status, odoo_state)
                        
                        # Prepare result
                        result = {
                            'uuid': recipient_uuids[i],
                            'state': odoo_state,
                            'kavenegar_messageid': str(entry.get("messageid", "")),
                        }
                        
                        # Add failure type for error states
                        if odoo_state == "server_error":
                            failure_type = KAVENEGAR_ERROR_TO_FAILURE_TYPE.get(kavenegar_status, "unknown")
                            result['failure_reason'] = entry.get("statustext", "Unknown error")
                            _logger.warning("SMS failed: UUID %s, Kavenegar status %s, reason: %s", 
                                          recipient_uuids[i], kavenegar_status, result['failure_reason'])
                        
                        results.append(result)
                        
            except (APIException, HTTPException) as e:
                _logger.error("Kavenegar API error: %s", str(e))
                # Mark all SMS as failed
                for uuid in recipient_uuids:
                    results.append({
                        'uuid': uuid,
                        'state': 'server_error',
                        'failure_reason': str(e),
                    })
                    
            except Exception as e:
                _logger.error("Unexpected error sending SMS: %s", str(e))
                # Mark all SMS as failed
                for uuid in recipient_uuids:
                    results.append({
                        'uuid': uuid,
                        'state': 'server_error',
                        'failure_reason': str(e),
                    })
        
        _logger.info("SMS batch completed. Results: %s", results)
        return results
    
    def _clean_phone_numbers(self, numbers):
        """Clean phone numbers for Kavenegar API"""
        cleaned = []
        for number in numbers:
            # Remove + and country code for Iranian numbers
            if number.startswith('+98'):
                cleaned.append('0' + number[3:])
            elif number.startswith('98'):
                cleaned.append('0' + number[2:])
            elif not number.startswith('0'):
                cleaned.append('0' + number)
            else:
                cleaned.append(number)
        return cleaned

    def _get_sms_api_error_messages(self):
        """Return error messages for Kavenegar SMS API"""
        error_dict = super()._get_sms_api_error_messages()
        error_dict.update({
            'kavenegar_error': 'خطا در ارسال پیامک از طریق کاوه نگار',
            'invalid_api_key': 'کلید API کاوه نگار نامعتبر است',
            'insufficient_credit': 'اعتبار کافی در حساب کاوه نگار موجود نیست',
            'kavenegar_blocked': 'پیامک توسط اپراتور مسدود شده است',
        })
        return error_dict 