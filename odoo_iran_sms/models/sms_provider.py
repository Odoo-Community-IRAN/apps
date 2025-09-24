# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from collections import defaultdict
from kavenegar import KavenegarAPI, HTTPException, APIException
from odoo import api, fields, models

from odoo.addons.odoo_iran_sms.tools.sms_api import SmsApiKavenegar, KAVENEGAR_SMS_STATUS_CODE


class KavenegarSmsProvider(models.Model):
    _name = "kavenegar.sms.provider"
    _inherit = ["mail.thread"]
    _description = "Kavenegar SMS Provider"

    name = fields.Char(required=True)
    api_key = fields.Char(required=True)
    sender_number = fields.Char(required=True)
    credit = fields.Float(readonly=True)
    latest_credit_update = fields.Datetime(readonly=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_ids = fields.Many2many(
        'res.company', 
        string='Companies',
        help='Companies that can use this SMS provider. Leave empty for all companies.'
    )

    @api.model
    def cron_update_sms_status(self):
        """Cron job to update SMS status from Kavenegar"""
        sms_to_update = self.env["sms.sms"].search([
            ("state", "=", "process"),
            ("messageid", "!=", False),
            ("write_date", ">", datetime.now() - timedelta(days=1)),
            ("write_date", "<", datetime.now() - timedelta(minutes=5))
        ])
        if sms_to_update:
            provider = self.search([('active', '=', True)], order="sequence asc", limit=1)
            if not provider:
                return
                
            messageids = ",".join(sms_to_update.mapped("messageid"))
            params = {"messageid": messageids}
            try:
                kn_api = KavenegarAPI(provider.api_key)
                response = kn_api.sms_status(params)

                for entry in response:
                    sms_record = self.env["sms.sms"].search([
                        ("messageid", "=", str(entry["messageid"])), 
                        ("to_delete", "=", False)
                    ])
                    if sms_record:
                        # Use the corrected status mapping
                        sms_status = KAVENEGAR_SMS_STATUS_CODE.get(entry["status"], "server_error")
                        vals = {"state": sms_status}
                        
                        # Handle different states properly
                        if sms_status in ["sent", "canceled"]:
                            vals["to_delete"] = True
                            vals["failure_type"] = False  # Clear any previous failure
                        elif sms_status == "server_error":
                            vals["failure_type"] = "sms_server"
                        elif sms_status == "process":
                            vals["failure_type"] = False  # Clear failure for processing SMS
                            
                        sms_record.write(vals)
            except (APIException, HTTPException) as e:
                provider.message_post(body=str(e), subject="Kavenegar API Exception")

    def action_credit_btn(self):
        """Update credit information from Kavenegar"""
        self.ensure_one()
        try:
            kn_api = KavenegarAPI(self.api_key)
            response = kn_api.account_info()
            self.credit = response["remaincredit"]
            self.latest_credit_update = datetime.now()
        except (APIException, HTTPException) as e:
            self.message_post(body=str(e), subject="Kavenegar API Exception")


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Define the base sms_provider field if it doesn't exist, or extend it if it does
    sms_provider = fields.Selection(
        string='SMS Provider',
        selection=[
            ('iap', 'Send via Odoo'),
            ('kavenegar', 'Send via Kavenegar'),
        ],
        default='iap',
    )
    
    def _get_sms_api_class(self):
        """Return the SMS API class to use for this company"""
        self.ensure_one()
        if self.sms_provider == 'kavenegar':
            return SmsApiKavenegar
        return super()._get_sms_api_class()


class SmsSms(models.Model):
    _inherit = "sms.sms"

    messageid = fields.Char(readonly=True, help="Kavenegar message ID")
    record_company_id = fields.Many2one('res.company', 'Company', ondelete='set null')
    
    # Add Kavenegar-specific failure types
    failure_type = fields.Selection(
        selection_add=[
            ('kavenegar_error', 'Kavenegar Error'),
            ('kavenegar_blocked', 'Message Blocked'),
        ],
        ondelete={'kavenegar_error': 'cascade', 'kavenegar_blocked': 'cascade'}
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Set company ID for SMS records"""
        for vals in vals_list:
            vals['record_company_id'] = vals.get('record_company_id') or self.env.company.id
        return super().create(vals_list)

    def _split_by_api(self):
        """Override to handle Kavenegar or IAP choice, which is company dependent"""
        # Group SMS by company (like Twilio does)
        sms_by_company = defaultdict(lambda: self.env['sms.sms'])
        todo_via_super = self.browse()
        
        for sms in self:
            sms_by_company[sms._get_sms_company()] += sms
            
        for company, company_sms in sms_by_company.items():
            if company.sms_provider == "kavenegar":
                # Use our Kavenegar SMS API
                sms_api = company._get_sms_api_class()(self.env)
                sms_api._set_company(company)
                yield sms_api, company_sms
            else:
                # Use default IAP SMS API
                todo_via_super += company_sms
                
        if todo_via_super:
            yield from super(SmsSms, todo_via_super)._split_by_api()

    def _get_sms_company(self):
        """Get the company for this SMS"""
        return self.mail_message_id.record_company_id or self.record_company_id or super()._get_sms_company()

    def _handle_call_result_hook(self, results):
        """Store Kavenegar message ID on SMS records"""
        kavenegar_sms = self.filtered(lambda s: s._get_sms_company().sms_provider == 'kavenegar')
        grouped_kavenegar_sms = kavenegar_sms.grouped("uuid")
        
        for result in results:
            sms = grouped_kavenegar_sms.get(result.get('uuid'))
            if sms and result.get('kavenegar_messageid'):
                sms.messageid = result['kavenegar_messageid']
                
        # Call super for non-Kavenegar SMS
        super(SmsSms, self - kavenegar_sms)._handle_call_result_hook(results)

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """Override _send to handle Kavenegar SMS sending"""
        try:
            result = super(SmsSms, self)._send(
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
                raise_exception=raise_exception,
            )
            return result
        except Exception as e:
            # Log the error but don't fail completely
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("SMS sending error: %s", str(e))
            if raise_exception:
                raise
            return True
