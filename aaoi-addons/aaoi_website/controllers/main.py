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
import io
import json
import logging
import mimetypes
import os
from ast import literal_eval

import werkzeug
from dateutil import relativedelta
from werkzeug import urls
from werkzeug.exceptions import NotFound

from odoo import _, fields
from odoo import http
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.http import request
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.misc import get_lang

logger = logging.getLogger(__name__)


class Portal(CustomerPortal):
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "birthday"]

    @http.route(['/my', '/my/home'], type='http', auth="public", website=True)
    def home(self, **kw):
        if request.env.user.has_group('base.group_public') and request.env.user.id != request.env.ref(
                'base.user_root').id:
            url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            return werkzeug.utils.redirect(urls.url_join(url, '/#'))
        else:
            values = self._prepare_portal_layout_values()
            return request.render("portal.portal_my_home", values)

    @http.route('/download', type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "mimetype", "res_model", "res_id", "type", "url"]
        )

        if attachment:
            attachment = attachment[0]

        if attachment["type"] == "url":
            if attachment["url"]:
                return request.redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            # we follow what is done in ir_http's binary_content for the extension management
            extension = os.path.splitext(attachment["name"] or '')[1]
            extension = extension if extension else mimetypes.guess_extension(attachment["mimetype"] or '')
            filename = attachment['name']
            filename = filename if os.path.splitext(filename)[1] else filename + extension
            return http.send_file(data, filename=filename, as_attachment=True)
        else:
            return request.not_found()

    # ------------------------------------------------------------
    # SNIPPETS PAGE
    # ------------------------------------------------------------

    @http.route(['/get_category'], type='json', auth="public", website=True)
    def get_category(self, **kwargs):
        categ_ids = request.env['event.tag.category'].sudo().search([], limit=1)
        if categ_ids:
            values = {
                'tag_ids': categ_ids.mapped('tag_ids')
            }
            lang = get_lang(request.env).code
            return request.env['ir.ui.view'].sudo().with_context(lang=lang)._render_template(
                "aaoi_website.dynamic_aaoi_category", values)
        else:
            return False

    @http.route(['/get_current_training'], type='json', auth="public", website=True)
    def get_current_training(self, **kwargs):
        event_ids = request.env['event.event'].sudo().search(
            [('website_published', '=', True), ('event_registrations_open', '=', True),
             ('date_begin', '>=', fields.Datetime.now())], order='date_begin desc').sorted(lambda x: x.date_begin)[:3]
        if event_ids:
            values = {
                'event_ids': event_ids,
            }
            lang = get_lang(request.env).code
            return request.env['ir.ui.view'].sudo().with_context(lang=lang)._render_template(
                "aaoi_website.dynamic_aaoi_current_training", values)
        else:
            return False

    @http.route(['/get_testimonial'], type='json', auth="public", website=True)
    def get_testimonial(self, **kwargs):
        testimonial_ids = request.env['event.testimonial'].sudo().search([], order='sequence')
        values = {
            'testimonial_ids': testimonial_ids
        }
        lang = get_lang(request.env).code
        return request.env['ir.ui.view'].sudo().with_context(lang=lang)._render_template(
            "aaoi_website.dynamic_aaoi_testimonial", values)

    @http.route(['/get_blog_event'], type='json', auth="public", website=True)
    def get_blog_event(self, **kwargs):
        event_id = request.env['event.event'].sudo().search(
            [('website_published', '=', True), ('event_registrations_open', '=', True),
             ('date_begin', '>=', fields.Datetime.now())], order='date_begin desc').sorted(lambda x: x.date_begin)[:1]
        post_ids = request.env['blog.post'].sudo().search([('website_published', '=', True)], limit=4, order='id desc')
        if event_id:
            values = {
                'event_id': event_id,
                'post_ids': post_ids,
                'json_scriptsafe': json_scriptsafe,
            }
            lang = get_lang(request.env).code
            return request.env['ir.ui.view'].sudo().with_context(lang=lang)._render_template(
                "aaoi_website.dynamic_aaoi_blog_event", values)
        else:
            return False

    # ------------------------------------------------------------
    # TRAINING PAGE
    # ------------------------------------------------------------

    @http.route(['/training', '/training/page/<int:page>'], type='http', auth="public", website=True)
    def portal_training(self, page=1, sortby=None, tags=None, search=None, search_in='content', ppg=False, **searches):
        values = self._prepare_portal_layout_values()
        event_obj = request.env['event.event']

        quantities_per_page = request.env['record.qty_per_page'].search([], order='sequence')

        domain = [('website_published', '=', True)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date_begin'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        # Default sortby event
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        search_tags = request.env['event.tag']
        if tags and len(eval(tags)) > 0:
            search_tags = search_tags.search([('id', 'in', eval(tags))])
            domain += [('tag_ids', 'in', search_tags.ids)]

        if ppg:
            try:
                ppg = int(ppg)
                searches['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            if quantities_per_page:
                ppg = quantities_per_page[0].name
            else:
                ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        # search
        if search and search_in:
            domain += [('name', 'ilike', search)]

        # Count for pager
        event_count = event_obj.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/training",
            url_args={'ppg': ppg, 'sortby': sortby, 'tags': tags},
            total=event_count,
            page=page,
            step=ppg
        )
        # Search the count to display, according to the pager data
        events = event_obj.search(domain, order=sort_order, limit=ppg, offset=pager['offset'])
        request.session['events_history'] = events.ids[:100]

        categ_ids = request.env['event.tag.category'].sudo().search([], limit=1)

        values.update({
            'literal_eval': literal_eval,
            'event_ids': events.sudo(),
            'tag_ids': categ_ids.mapped('tag_ids'),
            'pager': pager,
            'ppg': ppg,
            'ppr': ppr,
            'searches': searches,
            'search_tags': search_tags,
            'search_count': event_count,
            'page_name': 'training',
            'default_url': '/training',
            'quantities_per_page': quantities_per_page,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'this_year': fields.Datetime.now().strftime('%Y'),
        })
        return http.request.render("aaoi_website.trainings", values)

    @http.route(['/training/<model("event.event"):event>'], type='http', auth="public", website=True)
    def portal_training_details(self, event=None, **kw):
        planning_list = {}
        section_id = 0
        # If section line not exists, by default we set it to 'Day 1'
        if not any(line.display_type == 'line_section' for line in event.planning_ids):
            planning_list[0] = {'name': _('Day 1'), 'details': []}
        for line in event.planning_ids:
            if line.display_type == 'line_section':
                planning_list[line.id] = {'name': line.name, 'details': []}
                section_id = line.id
            else:
                planning_list[section_id]['details'].append(
                    {'hour': line.hour, 'sequence': line.sequence, 'description': line.description})
        values = {
            'event': event.sudo(),
            'planning_list': planning_list,
        }
        return request.render("aaoi_website.aaoi_training_details", values)

    # ------------------------------------------------------------
    # PLANNING PAGE
    # ------------------------------------------------------------

    @http.route(['/planning', '/planning/page/<int:page>'], auth='public', website="True")
    def portal_planning(self, page=1, sortby=None, year=None, month=None, ppg=False, **searches):
        values = self._prepare_portal_layout_values()
        event_obj = request.env['event.event']

        quantities_per_page = request.env['record.qty_per_page'].search([], order='sequence')

        domain = [('website_published', '=', True)]
        start_date = fields.Date.today() + relativedelta.relativedelta(day=1)
        if not year:
            end_date = start_date + relativedelta.relativedelta(months=+1, days=-1)
            domain += [('date_begin', '>=', start_date), ('date_begin', '<=', end_date)]
        else:
            start_date = start_date + relativedelta.relativedelta(year=eval(year), month=eval(month))
            end_date = start_date + relativedelta.relativedelta(months=+1, days=-1)
            domain += [('date_begin', '>=', start_date), ('date_begin', '<=', end_date)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date_begin'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        # Default sortby event
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if ppg:
            try:
                ppg = int(ppg)
                searches['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            if quantities_per_page:
                ppg = quantities_per_page[0].name
            else:
                ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        # Count for pager
        event_count = event_obj.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/planning",
            url_args={'ppg': ppg, 'sortby': sortby, 'year': year, 'month': month},
            total=event_count,
            page=page,
            step=ppg
        )
        # Search the count to display, according to the pager data
        events = event_obj.search(domain, order=sort_order, limit=ppg, offset=pager['offset'])
        request.session['plannings_history'] = events.ids[:100]

        values.update({
            'literal_eval': literal_eval,
            'event_ids': events.sudo(),
            'pager': pager,
            'ppg': ppg,
            'ppr': ppr,
            'searches': searches,
            'search_count': event_count,
            'page_name': 'planning',
            'default_url': '/planning',
            'quantities_per_page': quantities_per_page,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'this_year': fields.Datetime.now().strftime('%Y'),
        })
        return http.request.render("aaoi_website.plannings", values)

    @http.route('/get_plannings', type='json', auth='public', website=True)
    def get_plannings(self, **kwargs):
        event_obj = request.env['event.event']
        domain = [('website_published', '=', True)]
        start_date = fields.Date.today() + relativedelta.relativedelta(day=1)
        if not kwargs.get('year'):
            end_date = start_date + relativedelta.relativedelta(months=+1, days=-1)
            domain += [('date_begin', '>=', start_date), ('date_begin', '<=', end_date)]
        else:
            start_date = start_date + relativedelta.relativedelta(year=eval(kwargs.get('year')),
                                                                  month=eval(kwargs.get('month')))
            end_date = start_date + relativedelta.relativedelta(months=+1, days=-1)
            domain += [('date_begin', '>=', start_date), ('date_begin', '<=', end_date)]

        events = event_obj.search(domain)
        res = {request.env.user: [{'name': 'event', 'date': e.date_begin.strftime("%Y-%m-%d")} for e in events]}
        return json.dumps(list(res.values()))

    @http.route('/about-us', type='http', auth="public", website=True)
    def aboutus(self, **kw):
        values = {
            'page_name': 'aboutus',
        }
        return http.request.render("aaoi_website.aboutus", values)

    # ------------------------------------------------------------
    # FOOTER MENU REDIRECTING
    # ------------------------------------------------------------

    @http.route('/customized-training', type='http', auth="public", website=True)
    def customized_training(self, **kw):
        values = {
            'page_name': 'customized_training',
            'name': _('Customized training')
        }
        return http.request.render("aaoi_website.customized_training", values)

    @http.route('/cgu', type='http', auth="public", website=True)
    def cgu(self, **kw):
        values = {
            'page_name': 'cgu',
            'name': _('C.G.V / C.G.U')
        }
        return http.request.render("aaoi_website.cgu", values)

    @http.route('/contact', type='http', auth="public", website=True)
    def contact(self, **kw):
        values = {
            'page_name': 'contact',
            'name': _('Contact')
        }
        return http.request.render("aaoi_website.contact", values)

    @http.route('/legal-notice', type='http', auth="public", website=True)
    def legal_notice(self, **kw):
        values = {
            'page_name': 'legal_notice',
            'name': _('Legal Notice')
        }
        return http.request.render("aaoi_website.legal_notice", values)


class WebsiteEventController(WebsiteEventController):

    # ------------------------------------------------------------
    # REGISTRATION SUCCESS
    # ------------------------------------------------------------

    @http.route(['/event/<model("event.event"):event>/registration/success'], type='http', auth="public",
                methods=['GET'], website=True, sitemap=False)
    def event_registration_success(self, event, registration_ids):
        # fetch the related registrations, make sure they belong to the correct visitor / event pair
        visitor = request.env['website.visitor']._get_visitor_from_request()
        if not visitor:
            raise NotFound()
        attendees_sudo = request.env['event.registration'].sudo().search([
            ('id', 'in', [str(registration_id) for registration_id in registration_ids.split(',')]),
            ('event_id', '=', event.id),
            ('visitor_id', '=', visitor.id),
        ])
        return request.render("aaoi_website.registration_complete",
                              self._get_registration_confirm_values(event, attendees_sudo))
