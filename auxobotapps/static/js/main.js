(function ($) {
    "use strict";

    // initializing preloader
    $(window).on('load',function(){

        // date-picker
        if($('div').hasClass('birth-date-element')) {
            const myDatePicker = MCDatepicker.create({ 
                el: '#birth-date',
                dateFormat: 'MM/DD/YYYY',
                showCalendarDisplay: false,
                bodyType: 'inline',
                autoClose: false,
                closeOnBlur: true
            });
        }

        // testimonial slider 
        $(".recent-post-slider").owlCarousel({
            loop: true,
            margin: 0,
            nav: false,
            items: 1,
            slideTransition: 'linear',
            smartSpeed: 500,
            animateIn: 'fadeInDown',
            animateOut: 'fadeOutDown',
            autoplay: true,
            dotsClass: 'carousel-custom-dots',
            dotClass: 'owl-dot',
            mouseDrag: false,
            navText: ["<img src='assets/img/testimonial/left-arrow.png'>","<img src='assets/img/testimonial/right-arrow.png'>"],
            responsive: {
                1200: {
                    items: 1,
                    margin: 0
                },
                992: {
                    items: 2,
                    margin: 40
                },
                768: {
                    items: 2,
                    margin: 20
                }
            }
        });

        // recommended post slider
        $(".recommended-post-slider").owlCarousel({
            loop: true,
            margin: 40,
            nav: false,
            items: 2,
            slideTransition: 'linear',
            smartSpeed: 500,
            animateIn: 'fadeInDown',
            animateOut: 'fadeOutDown',
            autoplay: true,
            autoWidth:true,
            mouseDrag: true,
            dots: false
        });

        // AOS init
        AOS.init({
            once: true
        });
       
        
        var hei = $('.gm-scroll-view').height();
        $('.gm-scroll-view').on('scroll', function(){
            console.log($('scrolled' + '.gm-scroll-view').scrollTop());
            console.log('about offset' +$('#aboutUs').offset().top);
        });
        

        // preloader
        var preLoder = $(".preloader");
        preLoder.fadeOut(1000);

        // glitch animation remove
        var glitch_remove1 = $('.banner-7 .part-img .glitch.img-1');
        var glitch_remove2 = $('.banner-7 .part-img .glitch.img-2');
        setTimeout(function() {
            glitch_remove1.removeClass('activate');
        }, 2000);
        setTimeout(function() {
            glitch_remove2.removeClass('activate');
        }, 3500);

        // banner img animation
        setInterval(function(){ 
            $(".banner .part-img").addClass("animated");
            $(".banner-6 .part-img").addClass("animated");
            $(".banner-5 .banner-img").addClass('animated');
            $(".banner-7 .part-img .glitch").addClass('animated');
        }, 700); 

        //banner 10 animation for
        var ball_Img = $('.banner-10 .banner-bottom-player-img img.ball-img');
        var main_Img = $('.banner-10 .banner-bottom-player-img img.main-img');
        setInterval(function(){
            main_Img.addClass('animated');
        }, 1000); 

        function animatedOnBall() {
            ball_Img.addClass('animated');
        }

        var ball_interval = setInterval(animatedOnBall, 1500);
        ball_interval;

        setTimeout(function() {
            clearInterval(ball_interval);
        }, 1500);
        
        setTimeout(function() {
            ball_Img.removeClass('animated');
        }, 2500);
        
    });

    $(document).ready(function($){

        // testimonial slider 
        $(".testimonial-carousel").owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            items : 1,
            slideTransition: 'linear',
            smartSpeed: 500,
            animateIn: 'fadeInDown',
            animateOut: 'fadeOutDown',
            autoplay: false,
            dotsClass: 'carousel-custom-dots',
            dotClass: 'owl-dot',
            mouseDrag: false,
            navText: ["<img src='assets/img/testimonial/left-arrow.png'>","<img src='assets/img/testimonial/right-arrow.png'>"]
        });

        // count down
        var nodes = $('.timer');
        $.each(nodes, function (_index, value) {
            var date = $(this).data('date');

            setInterval(() => {

                var endTime = new Date(date);
                endTime = (Date.parse(endTime) / 1000);

                var now = new Date();
                now = (Date.parse(now) / 1000);

                var timeLeft = endTime - now;

                var days = Math.floor(timeLeft / 86400);
                var hours = Math.floor((timeLeft - (days * 86400)) / 3600);
                var minutes = Math.floor((timeLeft - (days * 86400) - (hours * 3600)) / 60);
                var seconds = Math.floor((timeLeft - (days * 86400) - (hours * 3600) - (minutes * 60)));

                if (hours < "10") { hours = "0" + hours; }
                if (minutes < "10") { minutes = "0" + minutes; }
                if (seconds < "10") { seconds = "0" + seconds; }

                $(value).find('.day').html(days);
                $(value).find('.hour').html(hours);
                $(value).find('.minute').html(minutes);
                $(value).find('.second').html(seconds);

            }, 1000);

        });

        const playing_bet_section = document.getElementsByClassName('playing-bet');
        if (playing_bet_section.length > 0) {
            $('.sports-menu').overlayScrollbars({
                resize          : null,
                sizeAutoCapable : true,
                paddingAbsolute : true,
                scrollbars : {
                    dragScrolling: true,
                    clickScrolling: false,
                    touchSupport :false,   
                },
                overflowBehavior : {
                    y :'hidden' 
                }
            }); 
        }
        
        

        // odometer
        $('.odometer').appear(function(e) {
            var odo = $(".odometer");
            odo.each(function() {
                var countNumber = $(this).attr("data-count");
                $(this).html(countNumber);
            });
        });

        // nav button change for homepage 9
        var navCloseIcon = 'assets/img/icon/nav-btn.png';
        var navOpenIcon = 'assets/img/icon/nav-btn-open.png';

        $('.header-9').find('button.nav-btn').on('click', function(){
            $('.header-9').find('button.nav-btn').find('img').fadeOut(10, function(){
                $('.header-9').find('button.nav-btn').find('img').attr('src', navOpenIcon);
            }).fadeIn();
            return false;
            
        });

        var myOffcanvas = $('#offcanvasExample');
        myOffcanvas.on('hidden.bs.offcanvas', function(){
            $('.header-9').find('button.nav-btn').find('img').fadeOut(10, function(){
                $('.header-9').find('button.nav-btn').find('img').attr('src', navCloseIcon);
            }).fadeIn();
            return false;
        });

        // testimonial slider 
        $(".banner-text-slide").owlCarousel({
            loop: true,
            margin: 0,
            nav: false,
            items: 1,
            slideTransition: 'linear',
            smartSpeed: 300,
            animateIn: 'fadeIn',
            animateOut: 'fadeOut',
            navText: ["<i class='fa-regular fa-chevrons-left'></i>","<i class='fa-regular fa-chevrons-right'></i>"]
        });

        var owl = $('.banner-text-slide');
        var page = 1;
        owl.owlCarousel();
        owl.on('changed.owl.carousel', function(event) {
            $('.slide-img img').css('opacity', '0');
            $('.slide-next-img img').css('opacity', '0');

            if( page == 1) {
                $('.slide-img img#slide-img-1').css('opacity', '1');
                $('.slide-next-img img#nxt-slide-img-2').css('opacity', '1');
                page = 2;
            }   
            
            else if(page == 2) {
                    $('.slide-img img#slide-img-2').css('opacity', '1');
                    $('.slide-next-img img#nxt-slide-img-0').css('opacity', '1');
                    page = 0;
                } 
            
            else if(page == 0) {
                    $('.slide-img img#slide-img-0').css('opacity', '1');
                    $('.slide-next-img img#nxt-slide-img-1').css('opacity', '1');
                page = 1;
            }
        });

        $('.customNextBtn').click(function() {
            owl.trigger('next.owl.carousel');
        })
        $('.customPrevBtn').click(function() {
            owl.trigger('prev.owl.carousel', [300]);
        })

        // language selection
        function lang_displaying(lang){
            $('.lang-display').html(lang);
        }

        var singleLangItem = $('.lang-item').find('.dropdown-item');
        singleLangItem.on('click', function(){
            lang_displaying($(this).html());
        });

        // initialize live clock
        const clock = new Clock();
        clock.start();

        
        // initialize video popup 
        var videoPlayBtnExists = $('.js-video-button').length > 0;
        if(videoPlayBtnExists) {
            $(".js-video-button").modalVideo({
                youtube:{
                    controls:0,
                    nocookie: true
                }
            });
        }

        // navbar toggler icon change
        $('.navbar-toggler').on('click', function(){
            if(!$('.navbar-toggler').hasClass('collapsed')) {
                $('.navbar-toggler').find('i').addClass('fa-bars-staggered', 500).removeClass('fa-bars');
            } else {
                $('.navbar-toggler').find('i').addClass('fa-bars').removeClass('fa-bars-staggered');
            }
        });


        $('.footer').find('.footer-bottom').prepend("<div class='back-to-top-btn'><a href='#'><i class='fa-solid fa-arrow-turn-up'></i></a></div>");

        $(window).on('scroll', function(){
            var footerSection = $('.footer').offset().top;
            var footerOffset = footerSection - $(window).innerHeight();
            var scroll = $(window).scrollTop();
            var backToTopBtn = $('.back-to-top-btn a');
            if ($(window).scrollTop() > 1500) {
                backToTopBtn.addClass('active');
            } else {
                backToTopBtn.removeClass('active');
            }
            if(scroll > footerOffset) {
                backToTopBtn.addClass('foot-on-bottom');
                $('.footer').find('.footer-bottom').find('.back-to-top-btn').find('a').addClass('active-plus');
            } else {
                backToTopBtn.removeClass('foot-on-bottom');
                $('.footer').find('.footer-bottom').find('.back-to-top-btn').find('a').removeClass('active-plus');
            }
         });

        var prev_scroll_position = $(window).pageYOffset;
        var mobile_fixed_header = $('.mobile-fixed-header');
        
        var fixed_top = $(".header");
        
    
        $(window).on("scroll", function(){
            var scroll_position = window.pageYOffset;
            var topbar = $('.topbar');
    
            if(scroll_position > 200) {
                fixed_top.addClass("animate__fadeInDown header-fixed");
            } 
    
            if(scroll_position > 2000) {
                    fixed_top.removeClass("animate__fadeInDown header-fixed");
            }
    
            if(prev_scroll_position > scroll_position) {
                if(scroll_position > 200) {
                    fixed_top.addClass("animate__fadeInDown header-fixed");
                    mobile_fixed_header.addClass('fixed');
                } else if (scroll_position < 200) {
                        fixed_top.removeClass("animate__fadeInDown header-fixed");
                        mobile_fixed_header.removeClass('fixed');
                }
            }
            prev_scroll_position = scroll_position;
        });

    });
    
}(jQuery));	