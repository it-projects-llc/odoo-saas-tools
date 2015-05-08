$(function() {

    $("input,textarea").jqBootstrapValidation({
        preventSubmit: true,
        submitError: function($form, event, errors) {
            // additional error messages or events
        },
        submitSuccess: function($form, event) {
            event.preventDefault(); // prevent default submit behaviour
            // get values from FORM
            var name = $("input#name").val();
            var email = $("input#email").val();
            var phone = $("input#phone").val();
            var message = $("textarea#message").val();
            var firstName = name; // For Success/Failure Message
            // Check for white space in name for Success/Fail message
            if (firstName.indexOf(' ') >= 0) {
                firstName = name.split(' ').slice(0, -1).join(' ');
            }
            $.ajax({
				type: 'POST',
				url: 'https://mandrillapp.com/api/1.0/messages/send.json',
				data: {
					'key': 'f_9NMMrABIuJKdw_MdtxSg',
				   'message': {
					   'from_email': 'shikher@shikherverma.com',
				   'to': [
				   {
					   'email': 'shikherverma@ymail.com',
				   'name': 'RECIPIENT NAME (OPTIONAL)',
				   'type': 'to'
				   }
				   ],
				   'autotext': 'true',
				   'subject': 'YOUR SUBJECT HERE!',
				   'html': 'YOUR EMAIL CONTENT HERE! YOU CAN USE HTML!'
				   }
				}
			}).done(function(response) {
				console.log(response); // if you're into that sorta thing
			});
            /*$.ajax({
				type: 'POST',
				url: 'https://mandrillapp.com/api/1.0/messages/send.json',
				data: {
						name: name,
						phone: phone,
						email: email,
						message: message
						'key': 'f_9NMMrABIuJKdw_MdtxSg',
						'message': 
							{
								'from_email': 'shikher@shikherverma.com',
								'to':
								[{
									'email': 'shikherverma@ymail.com',
									'name': 'RECIPIENT NAME (OPTIONAL)',
									'type': 'to'
								}],
								'autotext': 'true',
								'subject': 'YOUR SUBJECT HERE!',
								'html': 'YOUR EMAIL CONTENT HERE! YOU CAN USE HTML!'
							},
				 		success: function() 
						{
							// Success message
							$('#success').html("<div class='alert alert-success'>");
							$('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
							.append("</button>");
							$('#success > .alert-success')
							.append("<strong>Your message has been sent. </strong>");
							$('#success > .alert-success')
							.append('</div>');
							//clear all fields
							$('#contactForm').trigger("reset");
						},
						error: function() 
						{
							// Fail message
							$('#success').html("<div class='alert alert-danger'>");
							$('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
							.append("</button>");
							$('#success > .alert-danger').append("<strong>Sorry " + firstName + ", it seems that my mail server is not responding. Please try again later!");
							$('#success > .alert-danger').append('</div>');
							//clear all fields
							$('#contactForm').trigger("reset");
						},
				}
                //url: "././mail/contact_me.php",
                //type: "POST",
                  data: {
                    name: name,
                    phone: phone,
                    email: email,
                    message: message
                },
                cache: false,
                success: function() {
                    // Success message
                    $('#success').html("<div class='alert alert-success'>");
                    $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-success')
                        .append("<strong>Your message has been sent. </strong>");
                    $('#success > .alert-success')
                        .append('</div>');

                    //clear all fields
                    $('#contactForm').trigger("reset");
                },
                error: function() {
                    // Fail message
                    $('#success').html("<div class='alert alert-danger'>");
                    $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-danger').append("<strong>Sorry " + firstName + ", it seems that my mail server is not responding. Please consider sending an email to contact@shikherverma.com");
                    $('#success > .alert-danger').append('</div>');
                    //clear all fields
                    $('#contactForm').trigger("reset");
                },
            })*/
        },
        filter: function() {
            return $(this).is(":visible");
        },
    });

    $("a[data-toggle=\"tab\"]").click(function(e) {
        e.preventDefault();
        $(this).tab("show");
    });
});

/*When clicking on Full hide fail/success boxes */
$('#name').focus(function() {
    $('#success').html('');
});
