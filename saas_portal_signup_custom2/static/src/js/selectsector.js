odoo.define('saas_portal_signup_custom2.selectsector', function(require){
    "use strict";

	$( document ).ready(function(){
	    $.getScript('http://gregfranko.com/jquery.selectBoxIt.js/js/jquery.selectBoxIt.min.js').done(function(script, textStatu) {
		$("#selectsector").selectBoxIt({
		    theme: "default",
		    defaultText: "Select",
		    autoWidth: false,
		});
	    });
    if ($('.field-confirm_password').length) {
      $('.oe_website_login_container').css(width, '970px !important;');
    }
	});
});
