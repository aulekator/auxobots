/**
  * selectImages
  * menuleft
  * tabs
  * collapse_menu
  * showpass
  * select_colors_theme
  * icon_function
  * box_search
  * variant_picker
  * fullcheckbox
  * preloader
*/

; (function ($) {

  "use strict";

  var selectImages = function () {
    if ($(".image-select").length > 0) {
      const selectIMG = $(".image-select");
      selectIMG.find("option").each((idx, elem) => {
        const selectOption = $(elem);
        const imgURL = selectOption.attr("data-thumbnail");
        if (imgURL) {
          selectOption.attr(
            "data-content",
            "<img src='%i'/> %s"
              .replace(/%i/, imgURL)
              .replace(/%s/, selectOption.text())
          );
        }
      });
      selectIMG.selectpicker();
    }
  };

  var menuleft = function () {
    if ($('div').hasClass('section-menu-left')) {
      var bt = $(".section-menu-left").find(".has-children");
      bt.on("click", function () {
        var args = { duration: 200 };
        if ($(this).hasClass("active")) {
          $(this).children(".sub-menu").slideUp(args);
          $(this).removeClass("active");
        } else {
          $(".sub-menu").slideUp(args);
          $(this).children(".sub-menu").slideDown(args);
          $(".menu-item.has-children").removeClass("active");
          $(this).addClass("active");
        }
      });
      $('.sub-menu-item').on('click', function(event){
        event.stopPropagation();
      });
    }
  };

  var tabs = function(){
    $('.widget-tabs').each(function(){
        $(this).find('.widget-content-tab').children().hide();
        $(this).find('.widget-content-tab').children(".active").show();
        $(this).find('.widget-menu-tab').find('li').on('click',function(){
            var liActive = $(this).index();
            var contentActive=$(this).siblings().removeClass('active').parents('.widget-tabs').find('.widget-content-tab').children().eq(liActive);
            contentActive.addClass('active').fadeIn("slow");
            contentActive.siblings().removeClass('active');
            $(this).addClass('active').parents('.widget-tabs').find('.widget-content-tab').children().eq(liActive).siblings().hide();
        });
    });
  };

  $('ul.dropdown-menu.has-content').on('click', function(event){
    event.stopPropagation();
  });
  $('.button-close-dropdown').on('click', function(){
    $(this).closest('.dropdown').find('.dropdown-toggle').removeClass('show');
    $(this).closest('.dropdown').find('.dropdown-menu').removeClass('show');
  });

  var collapse_menu = function () {
    $(".button-show-hide").on("click", function () {
      $('.layout-wrap').toggleClass('full-width');
    })
  }

  var showpass = function() {
    $(".show-pass").on("click", function () {
      $(this).toggleClass("active");
      var input = $(this).parents(".password").find(".password-input");

      if (input.attr("type") === "password") {
        input.attr("type", "text");
      } else if (input.attr("type") === "text") {
        input.attr("type", "password");
      }
    });
  }

  var select_colors_theme = function () {
    if ($('div').hasClass("select-colors-theme")) {
      $(".select-colors-theme .item").on("click", function (e) {
        $(this).parents(".select-colors-theme").find(".active").removeClass("active");
        $(this).toggleClass("active");
      })
    }
  }

  var icon_function = function () {
    if ($('div').hasClass("list-icon-function")) {
      $(".list-icon-function .trash").on("click", function (e) {
        $(this).parents(".item-row").remove();
      })
    }
  }

  var box_search=function(){
        
    $(document).on('click',function(e){
      var clickID=e.target.id;if((clickID!=='s')){
          $('.box-content-search').removeClass('active');
      }});
    $(document).on('click',function(e){
        var clickID=e.target.class;if((clickID!=='a111')){
            $('.show-search').removeClass('active');
    }});
        
    $('.show-search').on('click',function(event){
      event.stopPropagation();}
    );
    $('.search-form').on('click',function(event){
      event.stopPropagation();}
    );
    var input =  $('.header-dashboard').find('.form-search').find('input');
    input.on('input', function() {
      if ($(this).val().trim() !== '') {
        $('.box-content-search').addClass('active');
      } else {
        $('.box-content-search').removeClass('active');
      }
    });
   
  }

  var preloader = function () {
    setTimeout(function () {
    $("#preload").fadeOut("slow", function () {
        $(this).remove();
    });
    }, 300);
  };

  var variant_picker = function () {
    if ($(".variant-picker-item").length) {
      $(".variant-picker-item label").on("click", function (e) {
        $(this)
          .closest(".variant-picker-item")
          .find(".variant-picker-label-value")
          .text($(this).data("value"));
      });
    }
  };

  var fullcheckbox = function () {
    $('.total-checkbox').on('click', function () {
      if ( $(this).is(':checked') ) {
        $(this).closest('.wrap-checkbox').find('.tf-table-item').addClass("checked");
        $(this).closest('.wrap-checkbox').find('.checkbox-item').prop('checked', true);
      } else {
        $(this).closest('.wrap-checkbox').find('.tf-table-item').removeClass("checked");
        $(this).closest('.wrap-checkbox').find('.checkbox-item').prop('checked', false);
      }
    });

    $('.tf-table-item .checkbox-item').on('click', function () {
      $(this).closest('.tf-table-item').toggleClass("checked");
    });
  };

  var counter = function () {
    if ($(document.body).hasClass("counter-scroll")) {
      var a = 0;
      var oTop = $(".counter").offset().top - window.innerHeight;

      if (a == 0 && oTop < 500) {
        if ($().countTo) {
          $(".counter")
            .find(".number")
            .each(function () {
              var to = $(this).data("to"),
                speed = $(this).data("speed");
              $(this).countTo({
                to: to,
                speed: speed,
              });
            });
        }
        a = 1;
      }
      $(window).scroll(function () {
        if (a == 0 && $(window).scrollTop() > oTop) {
          if ($().countTo) {
            $(".counter")
              .find(".number")
              .each(function () {
                var to = $(this).data("to"),
                  speed = $(this).data("speed");
                $(this).countTo({
                  to: to,
                  speed: speed,
                });
              });
          }
          a = 1;
        }
      });
    }
  };

  var sort = function () {
    $(".title-sort .btn-key-sort").click(function() {
      let columnIndex = $(this).data("index");
      let type = $(this).data("type");
      let table = $(".content-sort tbody");
      let rows = table.find("tr").toArray();
      let isAscending = $(this).data("order") === "asc";
      
      rows.sort((rowA, rowB) => {
          let cellA = $(rowA).children("td").find(".key-sort").eq(columnIndex).text().trim();
          let cellB = $(rowB).children("td").find(".key-sort").eq(columnIndex).text().trim();
          
          if (type === "number") {
              return isAscending ? (Number(cellA) - Number(cellB)) : (Number(cellB) - Number(cellA));
          } else {
              return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
          }
      });
      
      table.append(rows);
      $(this).data("order", isAscending ? "desc" : "asc");
    });
  }

  // Dom Ready
  $(function () {

    selectImages();
    menuleft();
    tabs();
    collapse_menu();
    showpass();
    select_colors_theme();
    icon_function();
    box_search();
    variant_picker();
    fullcheckbox();
    counter();
    sort();
    preloader();
    
  });

})(jQuery);
