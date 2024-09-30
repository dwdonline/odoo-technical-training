# -*- coding: utf-8 -*-
# Estate property offer model

from odoo import fields, models

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'

    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', required=True)
    price = fields.Float(required=True)
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused'), ('pending', 'Pending')],
        default='pending',
        required=True
    )
    validity = fields.Integer(string='Offer Validity (days)', default=7, required=True)
    date_deadline = fields.Date(string='Offer Deadline', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)