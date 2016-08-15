openerp.saas_client = function(instance){
    var _t = instance.web._t,
       _lt = instance.web._lt;

    instance.web.WebClient.include({
        _ab_location: function(dbuuid) {
            var ab_register = _.str.sprintf('%s/%s', this._ab_register_value, dbuuid);
            $('#announcement_bar_table').find('.url a').attr('href', ab_register);
            return _.str.sprintf(this._ab_location_value, dbuuid);
        },
        show_annoucement_bar: function(){
            var self = this;
            var config_parameter = new instance.web.Model('ir.config_parameter');
            var _super = self._super;
            return config_parameter.call('search_read', [[['key', 'in', ['saas_client.ab_location', 'saas_client.ab_register']]], ['key', 'value']]).then(function(res) {
                _.each(res, function(r){
                    if (r.key == 'saas_client.ab_location'){
                        self._ab_location_value = r.value;
                    } else if (r.key == 'saas_client.ab_register'){
                        self._ab_register_value = r.value;
                    }
                });
                if (!self._ab_location_value)
                    return;
                _super.apply(self);
        });
        }
    });
};