(function ($) {
    
    var tfLineChart = (function () {
  
      var chartBar = function () {
      
        var options = {
            chart: {
              height: 337,
              type: "area",
              zoom: {
                enabled: false
              },
              toolbar: {
                show: false,
              },
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
            dataLabels: {
              enabled: false
            },
            colors: ["#C388F7"],
            series: [
              {
                name: "$",
                data: [45, 52, 68, 75, 89, 93, 120 , 145]
              }
            ],
            fill: {
              type: "gradient",
              gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.3,
                opacityTo: 0.9,
                stops: [0, 90, 100]
              }
            },
            yaxis: {
              show: false,
            },
            xaxis: {
              labels: {
                style: {
                  colors: '#A4A4A9',
                },
              },
              categories: [
                "02:00pm",
                "03:00pm",
                "04:00pm",
                "05:00pm",
                "06:00pm",
                "07:00pm",
                "08:00pm",
                "09:00pm",
              ]
            }
          };

        chart = new ApexCharts(
          document.querySelector("#line-chart-1"),
          options
        );
        if ($("#line-chart-1").length > 0) {
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