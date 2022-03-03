odoo.define('aaoi_event.portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.PortalCertificate = publicWidget.Widget.extend({
        selector: '.o_portal_certificate',
        events: {
            'submit': '_onSubmit',
        },
        /**
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments);
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _disableButton: function (button) {
            $(button).attr('disabled', true);
            $(button).children('.fa-lock').removeClass('fa-lock');
            $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
        },
        _onSubmit: function (e) {
            var button = $('#check_button');
            if ($('#security_code')[0].value.trim() != '') {
                this._disableButton(button);
            }
        },
    });

});