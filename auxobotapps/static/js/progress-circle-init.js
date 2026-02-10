(function ($) {
    "use strict";

    $('.second.circle').each(function() {
        var $this = $(this);
        var progress = $this.data('progress');
        var progressPercentage = progress * 100;
        $this.circleProgress({
            value: progress,
            fill: {
                gradient: ['#d03355','#fb7a6b']
            },
            thickness: 5,
            lineCap: 'round',
            emptyFill: 'rgb(247, 217, 222)',
            animation: {
                duration: 2000
            }
        }).on('circle-animation-progress', function(event, progress) {
            $(this).find('.parcentage-text').html(progressPercentage % 1 === 0 ? progressPercentage.toFixed(0) + '<i>%</i>' : progressPercentage.toFixed(1) + '<i>%</i>');
        });
    });

}(jQuery));	