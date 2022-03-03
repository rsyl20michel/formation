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

import base64

from odoo import fields, models, api, tools
from odoo.addons.http_routing.models.ir_http import slug
from odoo.modules.module import get_resource_path
from odoo.tools.translate import html_translate


class EventEvent(models.Model):
    _name = 'event.event'
    _inherit = ['event.event', 'image.mixin']

    def _default_logo(self):
        image_path = get_resource_path('website', 'static/src/img', 'website_logo.svg')
        with tools.file_open(image_path, 'rb') as f:
            return base64.b64encode(f.read())

    modality_id = fields.Many2one('event.modality', string='Modality')
    target_ids = fields.Many2many('event.target', string="Targets")
    provided_ids = fields.One2many('event.provided', 'event_id', string='Provided')
    planning_ids = fields.One2many('event.planning', 'event_id', string='Plannings')
    note = fields.Html(string='Note', store=True, compute="_compute_note", readonly=False, translate=html_translate,
                       sanitize_attributes=False, sanitize_form=False)
    duration = fields.Integer(string='Duration')
    logo = fields.Binary('Logo', default=_default_logo, help="Display this logo on the website.")
    unit = fields.Selection([
        ('day', 'day(s)'),
        ('week', 'week(s)'),
        ('month', 'month(s)'),
        ('year', 'year(s)')
    ], default='day')

    @api.model
    def _search_get_detail_all(self, website, order, options):
        search_fields = ['name']
        fetch_fields = ['name', 'website_url']
        domain = [website.website_domain()]
        # Rule must be reinforced because of sudo.
        domain.append([('website_published', '=', True)])
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text'},
        }
        return {
            'model': 'event.event',
            'base_domain': domain,  # categories are not website-specific
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-folder-o',
            'order': 'name desc, id desc' if 'name desc' in order else 'name asc, id desc',
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(fetch_fields, mapping, icon, limit)
        for event, data in zip(self, results_data):
            data['website_url'] = '/training/%s' % (slug(event))
        return results_data
