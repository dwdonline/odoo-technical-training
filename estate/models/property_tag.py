# -*- coding: utf-8 -*-
# Estate property tag model

from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'

    name = fields.Char(required=True)
    color = fields.Integer()