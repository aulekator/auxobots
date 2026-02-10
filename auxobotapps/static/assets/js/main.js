(function ($) {
    "use strict";

    // initializing preloader
    $(window).on('load',function(){

        // preloader
        var preLoder = $(".preloader");
        preLoder.fadeOut(1000);
        
    });

    $(document).ready(function($){

        // settings title change
        var icon = $('.setting-title-changed').find('.icon').find('img');
        var text = $('.setting-title-changed').find('.text');

        $('.settings-tab-button').find('.nav-link').each(function () {
            $(this).on('click', function () {
                var clickedTab = $(this);

                $('.setting-title-changed').find('.icon, .text').fadeOut(150, function () {
                if (clickedTab.hasClass('settings-privacy-tab')) {
                    icon.attr('src', 'assets/img/icon/privacy.png');
                    text.html('Privacy Settings');
                } else if (clickedTab.hasClass('settings-account-tab')) {
                    icon.attr('src', 'assets/img/icon/account-settings.png');
                    text.html('Account Settings');
                } else {
                    icon.attr('src', 'assets/img/icon/edit-profile.png');
                    text.html("Edit Haden's profile");
                }

                $(this).fadeIn(150);
                });
            });
        });



        // date-picker
        if($('div').hasClass('tranx-history-nav')) {
            const myDatePicker = MCDatepicker.create({ 
                el: '#started-date',
                dateFormat: 'DD/MM/YYYY',
                showCalendarDisplay: false,
                bodyType: 'inline',
                autoClose: true,
                closeOnBlur: true,
                customOkBTN: ''
            });

            // Add class when the calendar is opened
            myDatePicker.onOpen(() => {
                document.querySelector('#started-date').classList.add('calendar-open');
                document.querySelector('.calndr label[for="started-date"]').classList.add('open-label');
                document.querySelector('#end-date').classList.remove('calendar-open');
                document.querySelector('.calndr label[for="end-date"]').classList.remove('open-label');
            });

            // Remove class when the calendar is closed
            myDatePicker.onClose(() => {
                document.querySelector('#started-date').classList.remove('calendar-open');
                document.querySelector('.calndr label[for="started-date"]').classList.remove('open-label');
            });

            myDatePicker.onSelect(() => {
                document.querySelector('#started-date').classList.add('selected-date');
                document.querySelector('.calndr label[for="started-date"]').classList.add('selected-label');
            });

            myDatePicker.onClear(() => {
                document.querySelector('#started-date').classList.remove('selected-date');
                document.querySelector('.calndr label[for="started-date"]').classList.remove('selected-label');
            });

            const endDatePicker = MCDatepicker.create({ 
                el: '#end-date',
                dateFormat: 'MM/DD/YYYY',
                showCalendarDisplay: false,
                bodyType: 'inline',
                autoClose: true,
                closeOnBlur: true,
                customOkBTN: ''
            });

            // Add class when the calendar is opened
            endDatePicker.onOpen(() => {
                document.querySelector('#end-date').classList.add('calendar-open');
                document.querySelector('.calndr label[for="end-date"]').classList.add('open-label');
                document.querySelector('#started-date').classList.remove('calendar-open');
                document.querySelector('.calndr label[for="started-date"]').classList.remove('open-label');
            });

            // Remove class when the calendar is closed
            endDatePicker.onClose(() => {
                document.querySelector('#end-date').classList.remove('calendar-open');
                document.querySelector('.calndr label[for="end-date"]').classList.remove('open-label');
            });

            endDatePicker.onSelect(() => {
                document.querySelector('#end-date').classList.add('selected-date');
                document.querySelector('.calndr label[for="end-date"]').classList.add('selected-label');
            });

            endDatePicker.onClear(() => {
                document.querySelector('#end-date').classList.remove('selected-date');
                document.querySelector('.calndr label[for="end-date"]').classList.remove('selected-label');
            });

            // payment and transaction category selection
            var tranxDisplay = $('.tranx-history-nav').find('#transaction_categorey').find('.text');
            var tranxdefaultText = 'Transaction categorey';
            
            $('[aria-labelledby="transaction_categorey"]').find('.dropdown-item').on('click', function(e){
                e.preventDefault();
                var trnx_cat = $(this).text();
                tranxDisplay.html(trnx_cat);
                $('.tranx-history-nav').find('#transaction_categorey').addClass('selected');
            });

            var payment_mDisplay = $('.tranx-history-nav').find('#payment_method').find('.text');
            var payment_mDefaultText = 'payment method';
            
            $('[aria-labelledby="payment_method"]').find('.dropdown-item').on('click', function(e){
                e.preventDefault();
                var payment_m = $(this).text();
                payment_mDisplay.html(payment_m);
                $('.tranx-history-nav').find('#payment_method').addClass('selected');
            })


            // reset button 
            document.getElementById('all-reset').addEventListener('click', () => {
                myDatePicker.reset();
                endDatePicker.reset();
                
                document.querySelector('#started-date').classList.remove('selected-date');
                document.querySelector('.calndr label[for="started-date"]').classList.remove('selected-label');
                
                document.querySelector('#end-date').classList.remove('selected-date');
                document.querySelector('.calndr label[for="end-date"]').classList.remove('selected-label');

                $('.tranx-history-nav').find('#transaction_categorey').removeClass('selected');
                $('.tranx-history-nav').find('#payment_method').removeClass('selected');
                tranxDisplay.html(tranxdefaultText);
                payment_mDisplay.html(payment_mDefaultText);
            });
        }

        // wallet selection
        function dropdownSelect(selectedItem, selectedItemShowed) {
            selectedItem.find('.dropdown-item').on('click', function(e){
                e.preventDefault();
                if($(this).parent().siblings().find('.dropdown-item').hasClass('active')) {
                    $(this).addClass('active');
                    $(this).parent().siblings().find('.dropdown-item').removeClass('active');
                    selectedItemShowed.find('.dropdown-toggle').html($(this).html());
                }
            })
        }
        
        $('.wallet-select').find('.dropdown-menu').find('li').each(function(){
            dropdownSelect($(this), $('.wallet-select'));
            $(this).find('.dropdown-item').on('click', function(){    
                $('.wallet-select').find('.dropdown-toggle').addClass('selected-moment');
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
        


        
        // $('.scrollable').overlayScrollbars({
        //     // resize          : null,
        //     // sizeAutoCapable : true,
        //     // paddingAbsolute : true,
        //     // scrollbars : {
        //     //     dragScrolling: true,
        //     //     clickScrolling: false,
        //     //     touchSupport :false,   
        //     // },
        //     // overflowBehavior : {
        //     //     y :'hidden' 
        //     // }
        // }); 


        
            function pending_slips_scrollable() {
                if($('.db-elements').find('.pending-slips-scrollable').length > 0) {
                    $('.pending-slips-scrollable').overlayScrollbars({
                        paddingAbsolute : true,
                        scrollbars : {
                            dragScrolling: true,
                            clickScrolling: true,
                            touchSupport :true,   
                            snapHandle: true,
                        }
                    }); 
                }
            }
       

        
        if($(window).width() > 991 || $(window).width() < 767) {
            pending_slips_scrollable();
        }
        if($(window).width() > 575 || $(window).width() < 479) {
            pending_slips_scrollable();
        }

        if($(window).resize()){
            pending_slips_scrollable();
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