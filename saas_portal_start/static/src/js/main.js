$(document).ready(function () {
    // check that we are on /page/start page
    if (!$('.odoo_call_action_bg').length)
        return;

    var height = $(window).innerHeight();
    var headerHeight = $('header').innerHeight();
    if ($('#oe_main_menu_navbar').length)
        headerHeight += $('#oe_main_menu_navbar').innerHeight();
    $('.odoo_secondary_A').css('height', height);
    window.scrollTo(0, headerHeight);


    /* ======== START TRIAL WIDGET ======== */
    var plan_id = $("input[name='plan_id']").attr('value');
    var base_saas_domain = $("input[name='base_saas_domain']").attr('value');

    var db_sel = 'input.odoo_db_name';
    var getUrlVars= function() {
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for (var i = 0; i < hashes.length; i++) {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
        return vars;
    };
    var url_params = getUrlVars();
    var check_database = function($input) {
        var error = false;
        var db_name = $input.val().toLowerCase();
        if (!db_name) {
            $input.attr('data-content', "Please choose your domain name");
            error = true;
        }
        db_name = _.str.slugify(db_name);
        if (!error && (/\s/.test(db_name))) {
            $input.attr('data-content', "Spaces are not allowed in domain names");
            error = true;
        } else if (db_name.length < 4) {
            $input.attr('data-content', "Your domain must be at least 4 characters long");
            error = true;
        } else if(!/^([a-z0-9\-]{2,})$/.test(db_name)) {
            $input.attr('data-content', "Special characters are not allowed in domain names");
            error = true;
        }

        if (error) {
            $input.popover('show');
        }
        else {
            //$input.popover('hide');
            var params = {
                jsonrpc: '2.0',
                method: 'call',
                params: {dbname: db_name},
                id: _.uniqueId('r'),
            };

            var payload = {
                type: "POST",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(params),
                processData: false,
                url: '/saas_portal/trial_check'
            };
            var request = $.ajax(payload).done(
                function(response, textStatus, jqXhr) {
                    if (!response.result.error) {
                        var app = $input.attr('data-app') || url_params.app || '';
                        var cta_from = $input.attr('data-cta_from') || url_params.cta_from || false;

                        // Google analytics for goal
                        if (cta_from) {
                          var ce = new CustomEvent('gaw', {'detail': {'type': 'vpv', 'id': 'trial_start', 'params': {'page': _.str.sprintf('/stats/cta/trial_start/%s', cta_from)}}});
                          window.dispatchEvent(ce);
                        }

                        var ce = new CustomEvent('gaw', {'detail': {'type': 'vpv', 'id': 'trial_start', 'params': {'page': _.str.sprintf('/stats/trial_start/%s', app)}}});
                        window.dispatchEvent(ce);
                        var ce = new CustomEvent('gaw', {'detail': {'type': 'event', 'id': 'trial_start', 'params': {'category': 'saas trial', 'action':'start', 'label':'register' }}});
                        window.dispatchEvent(ce);

                        var lang = 'en_US';
                        var hosting = $input.attr('data-hosting') || url_params.hosting || '';
                        var offset = -(new Date().getTimezoneOffset());
                        // _.str.sprintf()'s zero front padding is buggy with signed decimals, so doing it manually
                        var browser_offset = (offset < 0) ? "-" : "+";
                        browser_offset += _.str.sprintf("%02d", Math.abs(offset / 60));
                        browser_offset += _.str.sprintf("%02d", Math.abs(offset % 60));

                        var new_url = _.str.sprintf('/saas_portal/add_new_client?lang=%s&dbname=%s&tz=%s&hosting=%s&app=%s&plan_id=%s',
                                                    lang, db_name, browser_offset, hosting, app, plan_id);
                        window.location = new_url;
                    }
                    else {
                        var db_url = 'https://'+db_name+'.'+base_saas_domain+'/web';
                        $input.attr('data-content', 'This name is already taken, sorry.<br/>If you are the owner, please <a href="'+db_url+'">sign in</a>.');
                        $input.popover('show');
                    }
                }
            ).fail(function(jqXHR, textStatus, errorThrown) {
                $input.attr('data-content', "New subscriptions are currently unavailable, please try again in a few minutes");
                $input.popover('show');
            });
        }
    };

    $('button#create_instance').on('click', function(event) {
        event.preventDefault();
        var $self = $(this);
        var $db_input = $self.parent().parent().find(db_sel);
        check_database($db_input);
    });

    $(db_sel).popover({html: true});
    $(db_sel).on('keyup', function() {
        var $input = $(this);
        $input.popover('hide');
    });

});