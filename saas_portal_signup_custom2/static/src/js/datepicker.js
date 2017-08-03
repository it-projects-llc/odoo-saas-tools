odoo.define('saas_portal_signup_custom2.yearpicker', function(require){
    "use strict";

	$( document ).ready(function(){
	    var date_input=$('input[name="establishment_year"]');
	    var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
	    var options={
		changeYear: true,
		changeMonth: false,
		showButtonPanel: true,
		dateFormat: 'yy',
		yearRange:"-100:+0",
		onClose: function(dateText, inst) {
		    var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
		    $(this).datepicker('setDate', new Date(year, 1));
		}
	    };
	    date_input.datepicker(options);
	    date_input.focus(function () {
		$(".ui-datepicker-calendar").hide();
		$(".ui-datepicker-month").hide();
		$(".ui-datepicker-next").hide();
		$(".ui-datepicker-prev").hide();
	    });

	    var birthdate_input=$('input[name="birthdate_date"]');
	    var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
	    var options={
		changeYear: true,
		changeMonth: true,
		yearRange:"-100:+0",
		format: 'mm/dd/yyyy',
		container: container,
		todayHighlight: true,
		autoclose: true,
	    };
	    birthdate_input.datepicker(options);

	});
});
