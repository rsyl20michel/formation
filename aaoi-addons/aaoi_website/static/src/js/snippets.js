odoo.define('aaoi_website.snippets', function (require) {
    'use strict';

    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    const {ReCaptcha} = require('google_recaptcha.ReCaptchaV3');

    /**
     * Snippets Mixin
     */
    var SnippetsMixin = publicWidget.Widget.extend({
        disabledInEditableMode: false,
        /**
         *
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.data = [];
        },
        /**
         *
         * @override
         */
        willStart: function () {
            return this._super.apply(this, arguments).then(
                () => Promise.all([
                    this._fetchData(),
                ])
            );
        },
        /**
         *
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments)
                .then(() => {
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
                    this._render();
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
                });
        },
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            /* Calling RPC to get datas from database */
            this.data = '';
        },
        /**
         *
         * @private
         */
        _render: function () {
            this.$el.html(this.data);
        },
        /**
         *
         * @override
         */
        destroy: function () {
            this._super.apply(this, arguments);
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
            this.$el.html('');
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
        },
    });

    publicWidget.registry.Category = SnippetsMixin.extend({
        selector: '.aaoi_category_section',
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            const res = await this._rpc({
                route: '/get_category',
            });
            this.data = res;
        },
    });

    publicWidget.registry.BlogEvent = SnippetsMixin.extend({
        selector: '.aaoi_blog_event_section',
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            const res = await this._rpc({
                route: '/get_blog_event',
            });
            this.data = res;
        },
    });

    publicWidget.registry.CurrentTraining = SnippetsMixin.extend({
        selector: '.aaoi_current_training_section',
        events: {
            'click .btn_current_training': '_onSubmit',
        },
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            const res = await this._rpc({
                route: '/get_current_training',
            });
            this.data = res;
        },
        /**
         *
         * @override
         */
        _onSubmit: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $form = $(ev.currentTarget).closest('form');
            var $button = $(ev.currentTarget).closest('[type="submit"]');
            var post = {};
            post["nb_register-" + $button.attr('id')] = "1";
            $button.attr('disabled', true);
            return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: 'static', keyboard: false});
                $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                $modal.appendTo('body').modal();
                $modal.on('click', '.js_goto_event', function () {
                    $modal.modal('hide');
                    $button.prop('disabled', false);
                });
                $modal.on('click', '.close', function () {
                    $button.prop('disabled', false);
                });
            });
        },
    });

    publicWidget.registry.Testimonial = SnippetsMixin.extend({
        selector: '.aaoi_testimonial_section',
        events: {
            'click .link_play': '_openModal',
        },
        /**
         *
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments)
                .then(() => {
                    let carousel = this.$el.find("#carouselTestimony");
                    carousel.carousel({interval: parseInt(carousel.attr("data-interval"))});
                });
        },
        /**
         * Fetches the data.
         * @private
         */
        async _fetchData(e) {
            const res = await this._rpc({
                route: '/get_testimonial',
            });
            this.data = res;
        },
        /**
         *
         * @override
         */
        _openModal: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            let $modal = $("#videoModal");
            if (ev.currentTarget.attributes['event-name']) {
                $modal.find('.oe_event_name')[0].innerHTML = ev.currentTarget.attributes['event-name'].value;
                $modal.find('form')[0].action = ev.currentTarget.attributes['form-action'].value;
                $modal.find('iframe')[0].src = ev.currentTarget.attributes['video-url'].value + '?autoplay=1';
                $modal.modal('show');
                $modal.on('hidden.bs.modal', () => {
                    $modal.find('iframe').attr('src', '');
                });
            }
        },
    });

    publicWidget.registry.NewsLetter = publicWidget.extend({
        selector: '.s_newsletter_block',
        read_events: {
            'click .js_subscribe_btn': '_onSubscribeClick',
        },
        /**
         * @constructor
         */
        init: function () {
            this._super(...arguments);
            this._recaptcha = new ReCaptcha();
            this.mailingLists = [];
        },
        /**
         * @override
         */
        willStart: function () {
            this._recaptcha.loadLibs();
            return this._super(...arguments);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            var always = function (data) {
                var isSubscriber = data.is_subscriber;
                self.$('.js_subscribe_btn').prop('disabled', isSubscriber);
                self.$('input.js_subscribe_email')
                    .val(data.email || "")
                    .prop('disabled', isSubscriber);
                // Compat: remove d-none for DBs that have the button saved with it.
                self.$target.find('.js_subscribe').removeClass('d-none');
                self.$('.js_subscribe_btn').toggleClass('d-none', !!isSubscriber);
                self.$('.js_subscribed_btn').toggleClass('d-none', !isSubscriber);
            };
            if (this.$target.find('.js_subscribe').length) {
                return Promise.all([def, this._rpc({
                    route: '/website_mass_mailing/is_subscriber',
                    params: {
                        'list_id': this.$target.find('.js_subscribe').data('list-id'),
                    },
                }).then(always).guardedCatch(always)]);
            }
        },
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onSubscribeClick: async function () {
            var self = this;
            var $email = this.$(".js_subscribe_email:visible");

            if ($email.length && !$email.val().match(/.+@.+/)) {
                this.$target.find('.js_subscribe').addClass('o_has_error').find('.form-control').addClass('is-invalid');
                return false;
            }
            this.$target.find('.js_subscribe').removeClass('o_has_error').find('.form-control').removeClass('is-invalid');
            const tokenObj = await this._recaptcha.getToken('website_mass_mailing_subscribe');
            if (tokenObj.error) {
                self.displayNotification({
                    type: 'danger',
                    title: _t("Error"),
                    message: tokenObj.error,
                    sticky: true,
                });
                return false;
            }
            this._rpc({
                route: '/website_mass_mailing/subscribe',
                params: {
                    'list_id': this.$target.find('.js_subscribe').data('list-id'),
                    'email': $email.length ? $email.val() : false,
                    recaptcha_token_response: tokenObj.token,
                },
            }).then(function (result) {
                let toastType = result.toast_type;
                if (toastType === 'success') {
                    self.$(".js_subscribe_btn").addClass('d-none');
                    self.$(".js_subscribed_btn").removeClass('d-none');
                    self.$('input.js_subscribe_email').prop('disabled', !!result);
                    const $popup = self.$target.find('.js_subscribe').closest('.o_newsletter_modal');
                    if ($popup.length) {
                        $popup.modal('hide');
                    }
                }
                self.displayNotification({
                    type: toastType,
                    title: toastType === 'success' ? _t('Success') : _t('Error'),
                    message: result.toast_content,
                    sticky: true,
                });
            });
        },
    });

    /**
     * Download automatically generic catalog
     */
    publicWidget.registry.Contactus = publicWidget.Widget.extend({
        selector: '#contactus_form',
        events: {
            'click .s_website_form_send': '_onSubmit',
        },
        /**
         * @constructor
         */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.website_company_id = session.website_company_id || 1;
        },
        /**
         * @private
         */
        _onSubmit: function (e) {
            let disabled = false;
            let urlParams = new URLSearchParams(window.location.search);
            let learn_more = urlParams.get('learn_more');
            $("#contactus_form")[0].querySelectorAll("[required]").forEach(function (e) {
                let value = e.value;
                if ((value) && (value.trim() != '')) {
                    disabled = true;
                } else {
                    disabled = false;
                    return false
                }
                ;
            });
            if (disabled && $("#contactus_form") && learn_more) {
                window.location = '/web/content/res.company/' + this.website_company_id + '/' + 'generic_catalog' + '?download=true';
            }
        },
    });

});