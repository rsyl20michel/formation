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
from random import randint

from odoo import models, fields


class EventTarget(models.Model):
    _name = 'event.target'
    _description = "Event Target"
    _order = "sequence"

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    color = fields.Integer(string='Color Index', default=lambda self: self._default_color())
