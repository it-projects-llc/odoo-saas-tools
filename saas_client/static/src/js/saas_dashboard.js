odoo.define('saas_client', function (require) {

var Widget = require('web.Widget');
var dashboard = require('web_settings_dashboard');

dashboard.Dashboard.include({
    init: function(parent, data){
        var ret = this._super(parent, data);
        this.all_dashboards.push('saas');
        return ret;
    },
    load_saas: function(data){
        return  new DashboardSaaS(this, data.saas).replace(this.$('.o_web_settings_dashboard_saas'));
    },
});

var DashboardSaaS = Widget.extend({

    template: 'DashboardSaaS',

    // events: {
    //     'click .o_pay_subscription': 'on_pay_subscription',
    // },

    init: function(parent, data){
        this.data = data;
        this.parent = parent;
        return this._super.apply(this, arguments);
    },

    // on_pay_subscription: function(){

    // },
});

});
