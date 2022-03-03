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

import logging

from odoo import http, _
from odoo.http import request

logger = logging.getLogger(__name__)


class ShareRoute(http.Controller):

    @http.route(['/certificate/<security_code>',
                 '/certificate'], type='http', auth='public', website=True)
    def certificate_portal(self, security_code=None):
        """
        Leads to a public portal displaying certificate datas for anyone with the security code.
        :param security_code: security code generate with hashlib.sha224
        """
        try:
            certificate_id = request.env['event.certificate'].sudo().search([('security_code', '=', security_code)])
            values = {'scan': False if security_code is None else True, 'certificate_id': certificate_id,
                      'company': request.env.user.company_id}
            return request.render('aaoi_event.certificate_page', values)
        except Exception:
            logger.exception("Failed to generate the certificate portal")
        return request.not_found()

    @http.route('/certificate/checking', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def checking(self, **kwargs):
        """
        Checking security code if exists in database
        :param kwargs:
        :return:
        """
        try:
            security_code = kwargs.get('security_code')
            if len(security_code) < 10:
                values = {'scan': False, 'certificate_id': False, 'company': request.env.user.company_id,
                          'error': _('Ensure the first 10-Digit is being entered correctly.')}
            else:
                certificate_id = request.env['event.certificate'].sudo().search(
                    [('security_code', 'like', security_code)]).filtered(
                    lambda x: x.security_code.startswith(security_code))
                values = {'scan': False, 'certificate_id': certificate_id or False,
                          'company': request.env.user.company_id,
                          'error': False if certificate_id else _(
                              'Ensure the first 10-Digit is being entered correctly.')}
            return request.render('aaoi_event.certificate_page', values)
        except Exception:
            logger.exception("Failed to generate the certificate portal")
        return request.not_found()
