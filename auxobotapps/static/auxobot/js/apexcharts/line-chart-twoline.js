(function ($) {
  
    var tfLineChart = (function () {
  
      var chartBar = function () {
      
        var options = {
            series: [{
            name: 'Item 01',
            data: [31, 90, 58, 70, 92, 89, 80,]
          }, {
            name: 'Item 02',
            data: [51, 45, -25, 51, 34, 2, 41,]
          },
          ],
            chart: {
            height: 207,
            type: 'line',
            stacked: true,
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
         
          legend: {
            show: false,
          },
          colors: ['#D4FE75', '#ffffff4d'],
          stroke: {
            curve: 'smooth',
            width: 1,
          },
          yaxis: {
            show: false,
          },
          xaxis: {
            labels: {
              style: {
                colors: '#95989D',
              },
            },
            categories: ["Jan", "Feb","Mar", "Apr","May", "Jun","Jul" ]
          },
          tooltip: {
            show: false,
          },
        };
  
        chart = new ApexCharts(
          document.querySelector("#line-chart-twoline"),
          options
        );
        if ($("#line-chart-twoline").length > 0) {
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