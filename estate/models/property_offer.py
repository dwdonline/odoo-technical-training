# -*- coding: utf-8 -*-
# Estate property offer model

from odoo import fields, models

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(required=True)
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused'), ('pending', 'Pending'), ('cancelled', 'Cancelled')],
        default='pending',
        required=True
    )
    offer_date = fields.Date(default=fields.Date.today, required=True)
    property_id = fields.Many2one('estate.property', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True, ondelete='cascade')
    validity = fields.Integer(string='Offer Validity (days)', default=7, required=True)
    deadline = fields.Date(required=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)

    # The action buttons action_accept_offer and action_refuse_offer are defined in the estate.property model
    def action_accept_offer(self):
        self.status = 'accepted'
        for offer in self:
            offer.property_id.selling_price = offer.price

    def action_refuse_offer(self):
        self.status = 'refused'

    def action_cancel_offer(self):
        self.status = 'cancelled'

    def action_pending_offer(self):
        self.status = 'pending'
