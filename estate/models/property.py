# -*- coding: utf-8 -*-
# Estate module for managing real estate properties and clients

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

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
    active = fields.Boolean(default=True)
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
    # total_offers = fields.Integer(compute="_compute_total_offers", string=" Total Offers")
    # def _compute_total_offers(self):
    #     for estate in self:
    #         estate.total_offers = len(estate.offer_ids)
    total_offers = fields.Integer(compute="_compute_total_offers", string=" Total Offers")
    offers_label = fields.Char(compute="_compute_offers_label", string="Offers Label")

    def _compute_total_offers(self):
        for estate in self:
            estate.total_offers = len(estate.offer_ids)

    def _compute_offers_label(self):
        for estate in self:
            if estate.total_offers < 1:
                estate.offers_label = "No Offers"
            else:
                estate.offers_label = f" Total Offers ({estate.total_offers})"
            
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

    # Delete property and all related offers
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_canceled(self):
        for estate in self:
            if estate in self:
                if estate.state not in ("new", "canceled"):
                    raise UserError(_("You cannot delete a property that is not new or canceled"))

    # Create property
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property = self.env["estate.property"].browse(vals["property_id"])
            if property.offer_ids:
                min_price = min(property.offer_ids.mapped("price"))
                if vals["price"] < min_price:
                    raise UserError(_("The offer must be higher than %s") % min_price)
                property.state = "offer_received"
        return super().create(vals_list)
    
    # MySQL constraint to ensure that the expected price is always lower than the selling price
    _sql_constraints = [
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive"),
        ("check_expected_price", "CHECK(expected_price >= 0)", "The expected price must be positive"),
        ("unique_name", "UNIQUE(name)", "The property title must be unique"),
    ]

    # Ensure that the selling price is not 90% lower than the expected price
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for estate in self:
            if (not float_is_zero(estate.selling_price, precision_rounding=0.01) and
                    float_compare(estate.selling_price, 0.9 * estate.expected_price, precision_rounding=0.01) < 0
                ):
                raise ValidationError(_("The selling price should not be lower than 90% of the expected price"))