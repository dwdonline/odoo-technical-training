# -*- coding: utf-8 -*-
# Estate module for managing real estate properties and clients

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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
       [("new", "New"), ("offer_received", "Offer Received"), ("offer_accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")],
        default="new",
        string="Status",
    )
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="State")
    city = fields.Char()
    postcode = fields.Char()

    # Many2one relation with the partner model
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")

    # Computed total area
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area")
    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for estate in self:
            estate.total_area = estate.garden_area + estate.living_area

    # Total offers
    total_offers = fields.Integer(compute="_compute_total_offers", string=" Total Offers")
    def _compute_total_offers(self):
        for estate in self:
            estate.total_offers = len(estate.offer_ids)
        # if there are no offers, set the string to "No offers"
        if estate.total_offers == 0:
            estate.total_offers = "No offers"

    # Computed best offer
    best_price = fields.Float(compute="_compute_best_price", string="Best Price")

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for estate in self:
            if estate.offer_ids:
                estate.best_price = max(estate.offer_ids.mapped("price")) # Get the highest price of all offers
            else:
                estate.best_price = 0

    # validity and date_deadline
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", string="Deadline to accept offers")
    validity = fields.Integer(default=7)
    def _compute_date_deadline(self):
        for estate in self:
            create_date = estate.create_date or fields.Date.today()
            estate.date_deadline = fields.Date.add(create_date, days=estate.validity)

    def _inverse_date_deadline(self):
        for estate in self:
            estate.validity = (estate.date_deadline - fields.Date.to_date(estate.create_date)).days

    # Onchange for garden
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = self.garden_orientation = False

    # Mark property as sold with action_sell_property and account for error
    def action_sell_property(self):
        for estate in self:
            if estate.state == "sold":
                raise UserError(_("This property is already sold"))
            if estate.state == "canceled":
                raise UserError(_("This property is canceled, so it cannot be sold"))
            estate.state = "sold"

    # Mark property as canceled with action_cancel_property
    def action_cancel_property(self):
        for estate in self:
            if estate.state == "sold":
                raise UserError(_("This property is already sold"))
            if estate.state == "canceled":
                raise UserError(_("This property is already canceled"))
            estate.state = "canceled"