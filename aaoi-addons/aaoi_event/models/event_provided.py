# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2022 eTech (<https://www.etechconsulting-mg.com/>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class EventProvided(models.Model):
    _name = 'event.provided'
    _description = "Event Provided"
    _order = "sequence"

    type_id = fields.Many2one('event.provided.type', string='Type')
    description = fields.Char(string='Description', translate=True)
    event_id = fields.Many2one('event.event', string='Event', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=0)


class EventProvidedType(models.Model):
    _name = 'event.provided.type'
    _description = "Event Provided Type"
    _order = "sequence"

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
