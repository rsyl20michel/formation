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
import datetime
import logging

from odoo.tools import get_lang, babel_locale_parse
from odoo.tools.misc import posix_to_ldml

logger = logging.getLogger(__name__)

from odoo import models, fields, api

import babel
import babel.dates
import pytz

import odoo
import odoo.addons

_logger = logging.getLogger(__name__)


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @api.model
    def format_datetime(self, value, tz=False, dt_format='medium', lang_code=False):
        """ Formats the datetime in a given format.

            :param {str, datetime} value: naive datetime to format either in string or in datetime
            :param {str} tz: name of the timezone  in which the given datetime should be localized
            :param {str} dt_format: one of “full”, “long”, “medium”, or “short”, or a custom date/time pattern compatible with `babel` lib
            :param {str} lang_code: ISO code of the language to use to render the given datetime
        """
        if not value:
            return ''
        if isinstance(value, str):
            timestamp = odoo.fields.Datetime.from_string(value)
        else:
            timestamp = value

        tz_name = tz or self.env.user.tz or 'UTC'
        utc_datetime = pytz.utc.localize(timestamp, is_dst=False)
        try:
            context_tz = pytz.timezone(tz_name)
            localized_datetime = utc_datetime.astimezone(context_tz)
        except Exception:
            localized_datetime = utc_datetime

        lang = get_lang(self.env, lang_code)

        locale = babel_locale_parse(lang.code or lang_code)  # lang can be inactive, so `lang`is empty
        if not dt_format:
            date_format = posix_to_ldml(lang.date_format, locale=locale)
            time_format = posix_to_ldml(lang.time_format, locale=locale)
            dt_format = '%s %s' % (date_format, time_format)

        # Babel allows to format datetime in a specific language without change locale
        # So month 1 = January in English, and janvier in French
        # Be aware that the default value for format is 'medium', instead of 'short'
        #     medium:  Jan 5, 2016, 10:20:31 PM |   5 janv. 2016 22:20:31
        #     short:   1/5/16, 10:20 PM         |   5/01/16 22:20
        # Formatting available here : http://babel.pocoo.org/en/latest/dates.html#date-fields
        return babel.dates.format_datetime(localized_datetime, dt_format, locale=locale)

    @api.model
    def format_time(self, value, tz=False, time_format='medium', lang_code=False):
        """ Format the given time (hour, minute and second) with the current user preference (language, format, ...)

            :param value: the time to format
            :type value: `datetime.time` instance. Could be timezoned to display tzinfo according to format (e.i.: 'full' format)
            :param tz: name of the timezone  in which the given datetime should be localized
            :param time_format: one of “full”, “long”, “medium”, or “short”, or a custom time pattern
            :param lang_code: ISO

            :rtype str
        """
        if not value:
            return ''

        if isinstance(value, datetime.time):
            localized_datetime = value
        else:
            if isinstance(value, str):
                value = odoo.fields.Datetime.from_string(value)
            tz_name = tz or self.env.user.tz or 'UTC'
            utc_datetime = pytz.utc.localize(value, is_dst=False)
            try:
                context_tz = pytz.timezone(tz_name)
                localized_datetime = utc_datetime.astimezone(context_tz)
            except Exception:
                localized_datetime = utc_datetime

        lang = get_lang(self.env, lang_code)
        locale = babel_locale_parse(lang.code)
        if not time_format:
            time_format = posix_to_ldml(lang.time_format, locale=locale)

        return babel.dates.format_time(localized_datetime, format=time_format, locale=locale)

    def formatLang(self, value, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False):
        """
            Assuming 'Account' decimal.precision=3:
                formatLang(value) -> digits=2 (default)
                formatLang(value, digits=4) -> digits=4
                formatLang(value, dp='Account') -> digits=3
                formatLang(value, digits=5, dp='Account') -> digits=5
        """

        if digits is None:
            digits = DEFAULT_DIGITS = 2
            if dp:
                decimal_precision_obj = self.env['decimal.precision']
                digits = decimal_precision_obj.precision_get(dp)
            elif currency_obj:
                digits = currency_obj.decimal_places

        if isinstance(value, str) and not value:
            return ''

        lang_obj = get_lang(self.env)

        res = lang_obj.format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)

        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = '%s %s' % (res, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = '%s %s' % (currency_obj.symbol, res)
        return res

    @api.model
    def get_mega_menu_infos(self):
        categ_ids = self.env['event.tag.category'].sudo().search([], limit=1)
        event_id = self.env['event.event'].sudo().search(
            [('website_published', '=', True), ('event_registrations_open', '=', True),
             ('date_begin', '>=', fields.Datetime.now())], order='date_begin desc').sorted(lambda x: x.date_begin)[:1]
        values = {
            'tag_ids': categ_ids.mapped('tag_ids'),
            'event_id': event_id
        }
        return values
