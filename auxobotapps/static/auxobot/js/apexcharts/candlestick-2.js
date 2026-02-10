
  (function ($) {
    
    var tfLineChart = (function () {
  
      var chartBar = function () {
      
        var options = {
            series: [{
              data: [
                { x: '06', y: [200000, 900000, 100000, 600000] },
                { x: '07', y: [300000, 600000, 200000, 400000] },
                { x: '08', y: [400000, 800000, 300000, 650000] },
                { x: '09', y: [200000, 700000, 400000, 500000] },
                { x: '10', y: [300000, 800000, 500000, 700000] },
                { x: '11', y: [400000, 900000, 600000, 800000] },
                { x: '12', y: [500000, 1000000, 700000, 900000] },
                { x: '13', y: [300000, 600000, 200000, 450000] },
                { x: '14', y: [400000, 900000, 300000, 800000] }
              ]
            }],
            chart: {
                type: 'candlestick',
                height: 350,
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
            xaxis: {
                type: 'category',
                labels: {
                    style: {
                    colors: '#888',
                    fontSize: '14px'
                    }
                }
            },
            plotOptions: {
                candlestick: {
                  colors: {
                    upward: '#C388F7',
                  }
                },
                bar: {
                  columnWidth: '24px'
                }
            },
            yaxis: {
                labels: {
                    style: {
                    colors: '#888',
                    fontSize: '14px'
                    },
                    formatter: function (value) {
                        return value / 1000 + 'k';
                    }
                },
                min: 100000,
                max: 1000000
            },
            grid: {
              borderColor: '#e0e0e0',
              strokeDashArray: 4
            }
          };

        chart = new ApexCharts(
          document.querySelector("#candlestick-2"),
          options
        );
        if ($("#candlestick-2").length > 0) {
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