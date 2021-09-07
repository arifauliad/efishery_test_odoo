from odoo import fields, models

class EfisherySaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_name = fields.Char()

class EfisheryConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    static_token = fields.Char(config_parameter='default.static_token', default='static_token')