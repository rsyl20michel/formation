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
    'name': "AAOI Website",
    'summary': 'Manage AAOI Website',
    'description': """
This apps helps to manage aaoi website.
=====================
    """,
    'author': "eTech Consulting",
    'website': "https://www.etechconsulting-mg.com/",
    'category': 'Website',
    'version': '0.1',

    'depends': [
        'aaoi_base',
        'aaoi_event',
        'website_mass_mailing',
    ],

    'data': [
        # Data
        'data/ir_model_data.xml',
        # Security

        # Wizards

        # Menus

        # Views
        'views/template.xml',
        'views/snippets.xml',
        'views/layout.xml',
        'views/portal_templates.xml',
        'views/trainings.xml',
        'views/plannings.xml',
        'views/aboutus.xml',
        'views/registration.xml',

    ],
    'demo': [
    ],
    'sequence': -10,
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
    'assets': {
        'web.assets_frontend': [
            'aaoi_website/static/src/vendors/owl-carousel/assets/owl.carousel.min.css',
            'aaoi_website/static/src/vendors/owl-carousel/assets/owl.theme.default.min.css',
            'aaoi_website/static/src/vendors/owl-carousel/owl.carousel.min.js',
            'aaoi_website/static/src/js/lib/pignose.calendar.min.js',
            'aaoi_website/static/src/js/snippets.js',
            'aaoi_website/static/src/js/portal.js',
            'aaoi_website/static/src/css/pignose.calendar.min.css',
            'aaoi_website/static/src/scss/home_template.scss',
            'aaoi_website/static/src/scss/layout.scss',
            'aaoi_website/static/src/scss/training.scss',
            'aaoi_website/static/src/scss/planning.scss',
            'aaoi_website/static/src/scss/aaoi.scss',
        ],
    }
}
