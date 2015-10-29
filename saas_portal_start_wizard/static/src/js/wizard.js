$(document).ready(function() {
    $('input,select').not("[type=submit]").jqBootstrapValidation();
    function init_page_plan_select() {
        var selected_class = 'btn-info';
        if ($('.plans-list').hasClass('has-error'))
            selected_class = 'btn-danger';

        var id = $('input[name="plan_id"]').val();
        var flag = true;
        $('.plans-list .btn').each(function(){
            if ($(this).data('planid') == id) {
                flag = false;
                $(this).removeClass("btn-default").addClass(selected_class);
            }
            return flag;
        });
        if (flag)
            $('#wizard-form.page_plan_select .tab-next').attr('disabled', 'disabled');
    }
    init_page_plan_select();

    $('.plans-list .btn').click(function(event){
        event.preventDefault();
        $('.plans-list .btn').each(function(){
            $( this ).removeClass('btn-info btn-danger').addClass("btn-default");
        });

        $(this).removeClass('btn-default').addClass("btn-info");

        var id = $( this ).data('planid');
        $('input[name="plan_id"]').val(id);

        $('.tab-next').removeAttr('disabled');
    });

    $('.addons-list a.btn').click(function(event){
        event.preventDefault();
        if ($(this).hasClass('btn-info')) {
            $(this).removeClass('btn-info').addClass('btn-default');
        } else {
            $(this).removeClass('btn-default').addClass('btn-info');
        }

        var list = "";
        $('.addons-list a.btn-info').each(function(){
            var name = $( this ).data('addon_name');
            list += name + ",";
        });

        list = list.slice(0, list.length-1);
        $('input[name="addons"]').val(list);
    });

//    function check_page_plan_confirm() {
//        var valid = true;
//
//        $('#wizard-form.page_plan_confirm .form-group').not('.optional').each(function(){
//            valid = valid && (!$(this).hasClass('has-error'));
//            valid = valid && ($('.form-control', this).val() != "");
//        });
//
//        if (valid)
//            $('#wizard-form.page_plan_confirm .tab-next').removeAttr("disabled");
//        else
//            $('#wizard-form.page_plan_confirm .tab-next').attr("disabled", "disabled");
//    }
//    check_page_plan_confirm();
//
//    $('#wizard-form.page_plan_confirm input.form-control').not('.optional').on('input', function(event){
//        var input = $(this);
//        var parent = input.parent();
//        var value = input.val();
//
//        if (value) {
//            parent.removeClass('has-error');
//        } else {
//            parent.addClass('has-error');
//        }
//
//        check_page_plan_confirm();
//    });

    $('#wizard-form.page_plan_confirm').on('change', "select[name='country_id']", function () {
        var $select = $("select[name='state_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>=1);
    });
    $('#wizard-form.page_plan_confirm').find("select[name='country_id']").change();
});
