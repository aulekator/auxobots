
  (function ($) {
    
    var tfLineChart = (function () {
  
      var chartBar = function () {
      
        var options = {
            series: [56, 15, 56, 56],
            chart: {
              type: 'donut',
              height: 180,
              animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 10,
                animateGradually: {
                    enabled: true,
                    delay: 10
                },
                dynamicAnimation: {
                    enabled: true,
                    speed: 10
                }
              } 
            },
            labels: ['Grocery', 'Shopping', 'Health', 'Rent'],
            colors: ['#90caf9', '#f4ff81', '#ce93d8', '#ba68c8'],
            legend: {
              show: false
            },
            dataLabels: {
              enabled: false
            },
            plotOptions: {
              pie: {
                donut: {
                  size: '45%'
                }
              }
            },
            tooltip: {
              y: {
                formatter: function (value) {
                  return value + '%';
                }
              }
            }
          };

        chart = new ApexCharts(
          document.querySelector("#donut-1"),
          options
        );
        if ($("#donut-1").length > 0) {
          chart.render();
        }
    };
  
    /* Function ============ */
    return {
        init: function () {},
  
        load: function () {
          chartBar();
        },
        resize: function () {},
      };
    })();
  
    jQuery(document).ready(function () {});
  
    jQuery(window).on("load", function () {
      tfLineChart.load();
    });

    jQuery(window).on("resize", function () {});
})(jQuery);