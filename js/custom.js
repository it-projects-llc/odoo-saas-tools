if ($('#fundraising_progress').length){
    var FUNDED = 4000 / 80000.0;
    var DONE = 2000 / 80000.0;

    var letters = [];
    $([1,2,3,4]).each(function(position, id){
        var f = new ProgressBar.Path('#funded' + id);
        var d = new ProgressBar.Path('#done' + id);
        // I made it directly in svg
        //f.set(0);
        //d.set(0);
        letters.push({
            'funded': f,
            'done': d
        });
    });
    function animate(type, value, options){
        var TOTAL = 4.0;
        $({val:0}).animate({val:TOTAL*value}, $.extend({
            step: function(now){
                var id = Math.floor(now);
                var lt;
                for (var i=0; i<id; i++){
                    lt = letters[i];
                    if (lt && !lt[type + '_filled']){
                        // fill previous letter completly
                        lt[type].set(1);
                        lt[type + '_filled'] = 1;
                    }

                }
                lt = letters[id];
                if (lt)
                    lt[type].set(now % 1);
                $('#'+type + '_progress').html( Math.round((100 * (now / TOTAL))) + ' %');

            }}, options));
    }
    function start(){
        animate('funded', FUNDED,{
            'duration': 5000
        });
        setTimeout(function(){
            animate('done', DONE,{
                'duration': 5000
            });
        }, 1000);
    }

    var started = false;
    $(window).scroll(function() {
        if (started)
            return;
        var windowHeight = jQuery( window ).height();
        var thisPos = $('#fundraising_progress').offset().top;
        var topOfWindow = $(window).scrollTop();
        if (topOfWindow + windowHeight - 200 > thisPos ) {
            started = true;
            start();
        }
    });

}
