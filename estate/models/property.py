# -*- coding: utf-8 -*-
# Estate module for managing real estate properties and clients

from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(string="Title", required=True, translate=True)
    description = fields.Text()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )
    active = fields.Boolean(default=False)
    state = fields.Selection(
        string="Status",
        selection=[("new", "New"), ("offer_received", "Offer Received"), ("offer_accepted", "Offer Accepted"), ("sold", "Sold")],
        default="new",
    )
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="State")
    city = fields.Char()
    postcode = fields.Char()
