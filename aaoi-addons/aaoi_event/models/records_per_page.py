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

from odoo import fields, models


class RecordPerPage(models.Model):
    _name = 'record.qty_per_page'
    _description = 'Quantity per page'

    name = fields.Integer(string='Quantity', required=True, default=10)
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('const_unique_name', 'unique(name)', 'The duplicates of Quantity values are not allowed!'),
        ('check_name', 'CHECK(name > 0)', 'The Quantity should be greater than 0.'),
    ]
