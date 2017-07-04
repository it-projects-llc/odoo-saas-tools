odoo.define('saas_portal_signup_custom2.recaptcha', function(require){
    "use strict";

	$( document ).ready(function(){
	    var $captchas = $('.g-recaptcha');

	    if ($captchas.length) {
		$.getScript('https://www.google.com/recaptcha/api.js?hl=vi');
	    }
	});
});
