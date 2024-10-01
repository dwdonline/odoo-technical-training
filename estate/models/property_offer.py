# -*- coding: utf-8 -*-
# Estate property offer model

from odoo import fields, models

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

    price = fields.Float(required=True)
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused'), ('pending', 'Pending')],
        default='pending',
        required=True
    )
    offer_date = fields.Date(default=fields.Date.today, required=True)
    property_id = fields.Many2one('estate.property', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    validity = fields.Integer(string='Offer Validity (days)', default=7, required=True)
    deadline = fields.Date(required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)