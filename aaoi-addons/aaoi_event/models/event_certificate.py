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
import hashlib

import io

try:
    import qrcode
except ImportError:
    qrcode = None

from odoo import models, fields, api

SIZE = 150


class EventCertificate(models.Model):
    _name = 'event.certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Certificate"

    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char(string='Name', index=True, compute='_compute_name')
    number = fields.Char(string='Number', index=True)
    type_id = fields.Many2one('event.certificate.type', string='Type')
    event_id = fields.Many2one('event.event', string="Event")
    partner_id = fields.Many2one('res.partner', string='Attendee', index=True)
    date = fields.Date(string="Date", default=lambda self: fields.Date.today(), tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    scores = fields.Float(string='Scores', default=0.0)
    hourly_volume = fields.Float(string='Hourly Volume', default=0.0)
    security_code = fields.Char(string='Security Code', tracking=True)
    qrcode = fields.Binary(attachment=False, store=True, compute='_compute_qrcode')

    # Documents
    certificate = fields.Binary(string='Certificate')
    certificate_filename = fields.Char()

    @api.model
    def create(self, vals):
        res = super(EventCertificate, self).create(vals)
        sequence = self.env['ir.sequence'].next_by_code('event.certificate')
        res.number = sequence
        if not res.security_code:
            res.security_code = self._generate_security_code(res.partner_id.name, res.number)
        return res

    def _generate_security_code(self, partner_name, number):
        string = '%s-$-%s' % (partner_name.strip(), number.strip())
        return str(hashlib.sha224(string.encode('utf-8')).hexdigest())

    @api.depends('event_id', 'partner_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s - %s' % (rec.event_id.name, rec.partner_id.name)

    @api.depends('security_code')
    def _compute_qrcode(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            qr_code_string = '%s/certificate/%s' % (base_url, rec.security_code)
            data = io.BytesIO()
            qrcode.make(qr_code_string.encode(), box_size=4).save(data, optimise=True, format='PNG')
            rec.qrcode = base64.b64encode(data.getvalue()).decode()

    @api.onchange('event_id')
    def _onchange_event_id(self):
        for rec in self:
            rec.user_id = rec.event_id.user_id.id if rec.event_id else False


class EventCertificateType(models.Model):
    _name = 'event.certificate.type'
    _description = "Certificate Type"

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
