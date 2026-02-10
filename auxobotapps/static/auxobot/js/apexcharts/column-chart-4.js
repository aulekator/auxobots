(function ($) {
  
    var tfLineChart = (function () {
  
      var chartBar = function () {
      
        var options = {
            series: [{
                name: '',
                data: [44, 55, 41, 67, 22, 43, 21, 44, 55, 41, 67]
            }, {
                name: '',
                data: [13, 23, 20, 8, 13, 27, 33, 13, 23, 20, 8]
            }, {
                name: '',
                data: [11, 17, 15, 15, 21, 14, 15, 11, 17, 15, 15]
            }],
            chart: {
                type: 'bar',
                height: 87,
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
            plotOptions: {
                bar: {
                columnWidth: '5px',
                },
            },
            xaxis: {
                labels: {
                    show: false,
                },
            },
            fill: {
                opacity: 1
            },
            stroke: {
                enabled: false,
            },
            legend: {
                show: false
            },
            grid: {
                yaxis: {
                    lines: {
                      show: false
                    }
                },
                xaxis: {
                    lines: {
                      show: false
                    }
                }
            },
            tooltip: {
                enabled: false,
            },
            yaxis: {
                show: false,
            },
            dataLabels: {
                enabled: false
            },
            colors: ['#161326','#A4A4A9','#FFFFFF'],
        };
  
        chart = new ApexCharts(
          document.querySelector("#column-chart-4"),
          options
        );
        if ($("#column-chart-4").length > 0) {
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