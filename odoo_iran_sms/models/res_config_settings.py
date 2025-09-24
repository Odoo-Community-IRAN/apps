# -*- coding: utf-8 -*-
# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_provider = fields.Selection(related='company_id.sms_provider', required=True, readonly=False)

    def action_open_kavenegar_sms_provider(self):
        """Open Kavenegar SMS Provider configuration"""
        return {
            'name': 'Kavenegar SMS Providers',
            'type': 'ir.actions.act_window',
            'res_model': 'kavenegar.sms.provider',
            'view_mode': 'list,form',
            'target': 'current',
        } 