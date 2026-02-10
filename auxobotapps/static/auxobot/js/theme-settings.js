; (function ($) {

    "use strict";
                
    var tflight =$('#logo_header').data('light');
    var tfdark =$('#logo_header').data('dark');

    // menu style
    var menu_style = function () {
        $(".menu-style .icon-hover").on("click", function () {
            $(".layout-wrap").addClass("menu-style-icon");
            $(".layout-wrap").removeClass("menu-style-icon-default");
        })
        if ($(".layout-wrap").hasClass("menu-style-icon")) {
            $(".menu-style").find(".icon-hover").prop("checked", true);
        }
        $(".menu-style .icon-default").on("click", function () {
            $(".layout-wrap").addClass("menu-style-icon-default");
            $(".layout-wrap").removeClass("menu-style-icon");
        })
        if ($(".layout-wrap").hasClass("menu-style-icon-default")) {
            $(".menu-style").find(".icon-default").prop("checked", true);
        }
        $(".menu-style .menu-click").on("click", function () {
            $(".layout-wrap").removeClass("menu-style-icon");
            $(".layout-wrap").removeClass("menu-style-icon-default");
        })
        if (!$(".layout-wrap").hasClass("menu-style-icon") && !$(".layout-wrap").hasClass("menu-style-icon-default") ) {
            $(".menu-style").find(".menu-click").prop("checked", true);
        }
    }

    // layout width style
    var layout_width = function () {
        $(".layout-width .boxed").on("click", function () {
            console.log('1');
            $(".layout-wrap").addClass("layout-width-boxed");
        })
        if ($(".layout-wrap").hasClass("layout-width-boxed")) {
            $(".layout-width").find(".boxed").prop("checked", true);
        }
        $(".layout-width .full").on("click", function () {
            $(".layout-wrap").removeClass("layout-width-boxed");
        })
        if (!$(".layout-wrap").hasClass("layout-width-boxed")) {
            $(".layout-width").find(".full").prop("checked", true);
        }
    }

    // menu position style
    var menu_position = function () {
        $(".menu-position .menu-fixed").on("click", function () {
            $(".layout-wrap").removeClass("menu-position-scrollable");
        })
        if (!$(".layout-wrap").hasClass("menu-position-scrollable")) {
            $(".menu-position").find(".menu-fixed").prop("checked", true);
        }
        $(".menu-position .menu-scrollable").on("click", function () {
            $(".layout-wrap").addClass("menu-position-scrollable");
        })
        if ($(".layout-wrap").hasClass("menu-position-scrollable")) {
            $(".menu-position").find(".menu-scrollable").prop("checked", true);
        }
    }

    // header position style
    var header_position = function () {
        $(".header-position .header-fixed").on("click", function () {
            $(".layout-wrap").removeClass("header-position-scrollable");
        })
        if (!$(".layout-wrap").hasClass("header-position-scrollable")) {
            $(".header-position").find(".header-fixed").prop("checked", true);
        }
        $(".header-position .header-scrollable").on("click", function () {
            $(".layout-wrap").addClass("header-position-scrollable");
        })
        if ($(".layout-wrap").hasClass("header-position-scrollable")) {
            $(".header-position").find(".header-scrollable").prop("checked", true);
        }
    }

    // loader position style
    var style_loader = function () {
        $(".style-loader .style-loader-on").on("click", function () {
            $(".layout-wrap").removeClass("loader-off");
        })
        if (!$(".layout-wrap").hasClass("loader-off")) {
            $(".style-loader").find(".style-loader-on").prop("checked", true);
        }
        $(".style-loader .style-loader-off").on("click", function () {
            $(".layout-wrap").addClass("loader-off");
        })
        if ($(".layout-wrap").hasClass("loader-off")) {
            $(".style-loader").find(".style-loader-off").prop("checked", true);
        }
    }

    // clear-all
    var clear1 = function () {
        $(".form-theme-style .button-clear-select").on("click", function () {
            $("body").removeClass("dark-theme");
            $(".theme-dark-light").find(".light").find("input").prop("checked", true);
            localStorage.toggled = "light-theme";   
            $(".layout-wrap").removeClass("menu-style-icon");
            $(".layout-wrap").removeClass("menu-style-icon-default");
            $(".menu-style").find(".menu-click").prop("checked", true);
            $(".layout-wrap").removeClass("layout-width-boxed");
            $(".layout-width").find(".full").prop("checked", true);
            $(".layout-wrap").removeClass("menu-position-scrollable");
            $(".menu-position").find(".menu-fixed").prop("checked", true);
            $(".layout-wrap").removeClass("header-position-scrollable");
            $(".header-position").find(".header-fixed").prop("checked", true);
            $(".layout-wrap").removeClass("loader-off");
            $(".style-loader").find(".style-loader-on").prop("checked", true);
        })
    }

    // setting theme color
    // ---------------------------------
    // colors-menu
    var colors_menu = function () {
        $(".colors-menu .color-fff").on("click", function () {
            $(".layout-wrap").attr("data-menu-background", "colors-menu-fff");
            $("#logo_header").attr({src:tfdark});
        })
        $(".colors-menu .color-1E293B").on("click", function () {
            $(".layout-wrap").attr("data-menu-background", "colors-menu-1E293B");
            $("#logo_header").attr({src:tflight});
        })
        $(".colors-menu .color-161326").on("click", function () {
            $(".layout-wrap").attr("data-menu-background", "colors-menu-161326");
            $("#logo_header").attr({src:tflight});
        })
        $(".colors-menu .color-3A3043").on("click", function () {
            $(".layout-wrap").attr("data-menu-background", "colors-menu-3A3043");
            $("#logo_header").attr({src:tflight});
        })
    }

    // colors-header
    var colors_header = function () {
        $(".colors-header .color-fff").on("click", function () {
            $(".layout-wrap").attr("data-colors-header", "colors-header-fff");
        })
        $(".colors-header .color-1E293B").on("click", function () {
            $(".layout-wrap").attr("data-colors-header", "colors-header-1E293B");
        })
        $(".colors-header .color-161326").on("click", function () {
            $(".layout-wrap").attr("data-colors-header", "colors-header-161326");
        })
        $(".colors-header .color-3A3043").on("click", function () {
            $(".layout-wrap").attr("data-colors-header", "colors-header-3A3043");
        })
    }

    // theme-primary
    var primary_theme = function () {
        $(".colors-theme-primary .color-2377FC").on("click", function () {
            $(".layout-wrap").attr("data-theme-primary", "theme-primary-2377FC");
        })
        $(".colors-theme-primary .color-C0FAA0").on("click", function () {
            $(".layout-wrap").attr("data-theme-primary", "theme-primary-C0FAA0");
        })
        $(".colors-theme-primary .color-35988D").on("click", function () {
            $(".layout-wrap").attr("data-theme-primary", "theme-primary-35988D");
        })
        $(".colors-theme-primary .color-7047D6").on("click", function () {
            $(".layout-wrap").attr("data-theme-primary", "theme-primary-7047D6");
        })
    }

    // theme-background
    var theme_background = function () {
        $(".colors-theme-background .color-FFFFFF").on("click", function () {
            $("body").attr("data-theme-background", "theme-background-FFFFFF");
        })
        $(".colors-theme-background .color-252E3A").on("click", function () {
            $("body").attr("data-theme-background", "theme-background-252E3A");
        })
        $(".colors-theme-background .color-1E1D2A").on("click", function () {
            $("body").attr("data-theme-background", "theme-background-1E1D2A");
        })
        $(".colors-theme-background .color-1B2627").on("click", function () {
            $("body").attr("data-theme-background", "theme-background-1B2627");
        })
    }

    // clear-all
    var clear2 = function ()  {
        $(".form-theme-color .button-clear-select").on("click", function () {
            $(".layout-wrap").attr("data-colors-header", "");
            $(".layout-wrap").attr("data-menu-background", "");
            $(".layout-wrap").attr("data-theme-primary", "");
            $("body").attr("data-theme-background", "");
            $(".select-colors-theme").find(".active").removeClass("active");
            $(".select-colors-theme").find(".default").addClass("active");
            $("#logo_header").attr({src:tflight});
        })
    }

  // Dom Ready
  $(function () {
    menu_style();
    layout_width();
    menu_position();
    header_position();
    style_loader();
    clear1();
    colors_menu();
    colors_header();
    primary_theme();
    theme_background();
    clear2();
  });

})(jQuery);

