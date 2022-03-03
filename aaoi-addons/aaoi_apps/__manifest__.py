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
{
    'name': "AAOI Apps",
    'summary': 'Manage AAOI Apps',
    'description': """
This apps helps to manage AAOI Apps.
=====================
    """,
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Website',
    'version': '0.1',

    'depends': [
        'aaoi_base',
        'aaoi_event',
        'aaoi_website',
    ],

    'data': [
        # data

        # security

        # views

        # reports

        # wizards

    ],
    'demo': [
    ],
    'sequence': -10,
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
