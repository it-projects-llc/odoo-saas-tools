odoo.define('saas_portal_signup_custom2.recaptcha', function(require){
    "use strict";

	$( document ).ready(function(){
	    var $captchas = $('.g-recaptcha');

	    if ($captchas.length) {
		var pathname_arr = window.location.pathname.split('/');
		if (pathname_arr.length == 2) {
		    $.getScript('https://www.google.com/recaptcha/api.js');
		} else {
		    var lang = pathname_arr[1];
		    if (lang == 'vi_VN') {
			$.getScript('https://www.google.com/recaptcha/api.js?hl=vi');
		    } else {
			$.getScript('https://www.google.com/recaptcha/api.js');
		    }
		}
	    }
	});
});
