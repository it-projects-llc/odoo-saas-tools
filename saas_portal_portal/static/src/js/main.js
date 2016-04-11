$(document).ready(function () {

    var client_id = $("input[name='client_id']").attr('value')
    var base_saas_domain = $("input[name='base_saas_domain']").attr('value')

    var new_domain_sel = 'input.new_domain_name';

    var check_database = function($input) {
        var error = false;
        var db_name = $input.val().toLowerCase();
        if (!db_name) {
            $input.attr('data-content', "Please choose your domain name");
            error = true;
        }
        if (!error && (/\s/.test(db_name))) {
            $input.attr('data-content', "Spaces are not allowed in domain names");
            error = true;
        } else if (db_name.length < 4) {
            $input.attr('data-content', "Your domain must be at least 4 characters long");
            error = true;
        } else if(!/^(?!:\/\/)([a-zA-Z0-9]+\.)?[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,6}?$/i.test(db_name)) {
            $input.attr('data-content', "Domain name isn't valid");
            error = true;
        }

        if (error) {
            $input.popover('show');
        }
        else {
            var new_url = _.str.sprintf('/saas_portal/rename_client?client_id=%s&dbname=%s',
                                        client_id, db_name);
            window.location = new_url;
        }
    };


	  $('button#change_domain').on('click', function(event) {
        event.preventDefault();
	      var $self = $(this);
	      var $db_input = $self.parent().parent().find(new_domain_sel);
        check_database($db_input)
	  });

	  $(new_domain_sel).popover({html: true});
	  $(new_domain_sel).on('keyup', function() {
        var $input = $(this);
        $input.popover('hide');
    });

})
