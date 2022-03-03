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
import re

from odoo import api
from odoo import fields, models

# Extract id from url path
RE_YOUTUBE = r"(?:\/embed)?\/([\w-]{10,12})"


class EventTestimonial(models.Model):
    _name = 'event.testimonial'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Testimonial"

    active = fields.Boolean('Active', default=True, tracking=True)
    sequence = fields.Integer('Sequence', default=0)
    name = fields.Char(string='Name', index=True, default='/')
    partner_id = fields.Many2one('res.partner', string='Attendee', index=True)
    event_id = fields.Many2one('event.event', string="Event")
    company_name = fields.Char(string='Company')
    short_description = fields.Char(string='Description', translate=True)
    video_url = fields.Char('Video URL',
                            help="Configure this URL so that event attendees can see your testimony in video!")
    thumbnail_url = fields.Char('Thumbnail URL', default=False, compute='_compute_thumbnail_url')
    thumbnail = fields.Binary('Thumbnail')

    @api.model
    def create(self, vals):
        res = super(EventTestimonial, self).create(vals)
        sequence = self.env['ir.sequence'].next_by_code('event.testimonial')
        res.name = sequence
        return res

    @api.depends('video_url')
    def _compute_thumbnail_url(self):
        for rec in self:
            # Youtube
            if any(url in rec.video_url for url in ['www.youtube.com', 'youtube.com', 'youtu.be']):
                id = re.findall(RE_YOUTUBE, rec.video_url)
                if len(id) > 0:
                    rec.thumbnail_url = "%s/%s/hqdefault.jpg" % ("http://img.youtube.com/vi", id[0])
            else:
                rec.thumbnail_url = False
