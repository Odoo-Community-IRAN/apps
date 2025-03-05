# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class TransactionTypeConfig(models.Model):
    _name = 'transaction.type.config'
    _description = 'Transaction Type Configuration'

    name = fields.Char('Name')
    transaction_type = fields.Selection(
        [('purchase', 'Purchase'), ('sale', 'Sale')],
        string="Transaction Type",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transaction_type_id = fields.Many2one(
        'transaction.type.config',
        string='Transaction Type',
        domain=[('transaction_type', 'in', ['purchase', 'sale'])],
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        transaction_type_id = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_currency_rate_update.transaction_type_id', default=False
        )

        if transaction_type_id:
            res.update(transaction_type_id=int(transaction_type_id))

        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        if self.transaction_type_id:
            config_parameter = self.env['ir.config_parameter'].sudo()
            config_parameter.set_param('odoo_currency_rate_update.transaction_type_id', self.transaction_type_id.id)
        else:
            config_parameter = self.env['ir.config_parameter'].sudo()
            config_parameter.set_param('odoo_currency_rate_update.transaction_type_id', False)
