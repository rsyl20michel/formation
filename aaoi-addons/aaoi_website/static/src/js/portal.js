odoo.define('aaoi_website.portal', function (require) {
    'use strict';

    var utils = require('web.utils');
    var ajax = require('web.ajax');
    var lang = utils.get_cookie('frontend_lang');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.TraningPortal = publicWidget.Widget.extend({
        selector: '.aaoi_trainings_container',
        events: {
            'click #tag_id': '_toggleFilterTags',
            'click #all_tags': '_toggleFilterAllTags',
        },
        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        /**
         * @private
         */
        _toggleFilterTags: function (e) {
            if (e.currentTarget.checked) {
                window.location = e.currentTarget.value;
            } else {
                let urlParams = new URLSearchParams(window.location.search);
                let tags = urlParams.get('tags');
                let current_tags = eval(tags).filter(x => x != parseInt(e.currentTarget.attributes['tag-id'].value));
                window.location = '/training?tags=[' + encodeURIComponent(current_tags) + ']';
            }
        },
        _toggleFilterAllTags: function (e) {
            if (e.currentTarget.checked) {
                $('#tag_id').checked = false;
                window.location = e.currentTarget.value;
            }
        },
    });

    publicWidget.registry.PlanningPortal = publicWidget.Widget.extend({
        selector: '.aaoi_plannings_container',
        events: {
            'click .btn_current_training': '_onSubmit',
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            this._fetch();
            return def;
        },

        /**
         * @private
         */
        _fetch: async function (e) {
            let events = await this._get_plannings();
            let urlParams = new URLSearchParams(window.location.search);
            let ppg = urlParams.get('ppg') || null;
            let year = urlParams.get('year');
            let month = urlParams.get('month');
            const d = new Date();
            $('.calendar').pignoseCalendar({
                // en, ko, fr, ch, de, jp, pt, fr
                lang: lang.indexOf('en') === 0 ? 'en' : 'fr',
                date: !year ? moment() : moment(year + '-' + month + '-' + d.getDate()),
                multiple: false,
                scheduleOptions: {
                    colors: {
                        event: '#B375BD'
                    }
                },
                schedules: JSON.parse(events)[0],
                select: function (date, context) {
                    console.log(date[0], date[1]);
                },
                page: function (info, context) {
                    /**
                     * @params context PignoseCalendarPageInfo
                     * @params context PignoseCalendarContext
                     * @returns void
                     */
                    window.location = '/planning?ppg=' + ppg + '&year=' + info.year + '&month=' + info.month;
                }
            });
        },
        _get_plannings: function (e) {
            let urlParams = new URLSearchParams(window.location.search);
            let year = urlParams.get('year');
            let month = urlParams.get('month');
            return this._rpc({
                route: '/get_plannings',
                params: {
                    year: year ? year : null,
                    month: month ? month : null
                },
            }).then(res => {
                return res;
            });
        },
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

    publicWidget.registry.TrainingDetailsPortal = publicWidget.Widget.extend({
        selector: '.aaoi_training_details_container',
        events: {
            'click .btn_current_training': '_onSubmit',
        },
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

    publicWidget.registry.AboutUsPortal = publicWidget.Widget.extend({
        selector: '.aaoi_aboutus_container',
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$el.find('#aaoi_team_snippet').owlCarousel({
                loop: true,
                margin: 24,
                nav: true,
                autoplay: true,
                autoplayHoverPause: true,
                responsive: {
                    0: {items: 1},
                    600: {items: 3},
                    1000: {items: 4}
                }
            })
            return def;
        },
    })
    ;

    $(document).ready(function () {
        if ($(window).width() < 769) {
            $(".aaoi_nav_item").click(function (e) {
                e.preventDefault();
                $(".aaoi_submenu_content").toggleClass("show");
            });
        }
    });
})
;