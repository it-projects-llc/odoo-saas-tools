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

    $('.tab-actions #wizard-goback').click(function(event){
        event.preventDefault();
        var $form = $("#wizard-form");
        var action = $("input[name='wizard_action']", $form);
        action.val('prev');
        $form.submit();
    });
//    $('.tab-actions #wizard-submit').click(function(event){
//        event.preventDefault();
//        var $form = $("#wizard-form");
//        $form.submit();
//    });

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

    $('#wizard-form.page_plan_confirm').on('change', "select[name='country_id']", function () {
        var $select = $("select[name='state_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>=1);
    });
    $('#wizard-form.page_plan_confirm').find("select[name='country_id']").change();

    var $payment = $("#payment_methods");
    $payment.on("click", "input[name='acquirer']", function (ev) {
            var payment_id = $(ev.currentTarget).val();
            $("div.oe_sale_acquirer_button[data-id]", $payment).addClass("hidden");
            $("div.oe_sale_acquirer_button[data-id='"+payment_id+"']", $payment).removeClass("hidden");
        })
        .find("input[name='acquirer']:checked").click();

    // When clicking on payment button: create the tx using json then continue to the acquirer
    $payment.on("click", 'button[type="submit"],button[name="submit"]', function (ev) {
      console.log("SaaS Start Wizard processing")
      ev.preventDefault();
      ev.stopPropagation();
      var $form = $(ev.currentTarget).parents('form');
      var acquirer_id = $(ev.currentTarget).parents('div.oe_sale_acquirer_button').first().data('id');
      var order_name = $('input[name="item_number"]', $form).val();
      if (! acquirer_id) {
        return false;
      }
      openerp.jsonRpc('/saas/pricing/payment/transaction/' + acquirer_id + '/' + order_name, 'call', {}).then(function (data) {
        $form.submit();
      });
   });
});
