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

from odoo import models, fields, api


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    total_certificates = fields.Integer(string="Certificates", compute='_count_total_certificates')
    birthday = fields.Date(string='Birthday', compute='_compute_birthday', readonly=False, store=True, tracking=14)

    @api.depends('partner_id')
    def _compute_birthday(self):
        for registration in self:
            if not registration.birthday and registration.partner_id:
                registration.birthday = registration._synchronize_partner_values(
                    registration.partner_id,
                    fnames=['birthday']
                ).get('birthday') or False

    def _count_total_certificates(self):
        for rec in self:
            rec.total_certificates = self.env['event.certificate'].search_count(
                [('partner_id', '=', self.partner_id.id)])

    def action_view_certificates(self):
        self.ensure_one()
        action = self.env.ref('aaoi_event.event_certificate_action').read()[0]
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        action['context'] = {'default_partner_id': self.partner_id.id,
                             'default_event_id': self.event_id.id}
        return action
