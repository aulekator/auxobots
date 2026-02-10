$(document).ready(function($){

    // selection input
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

    // scroll in function in medium mobile
    $(window).on("scroll", function(){
        var processing_steps = $('.processing-steps');
        var poklotto_register_form = $('#poklotto_register_form');
        var changeForm_title = $('h3.steps-heading-title');
        var offsetTop = poklotto_register_form.offset().top;
        if($(window).scrollTop() > offsetTop) {
            processing_steps.addClass('top-fixed animate__animated animate__fadeInDown');
            changeForm_title.addClass('steps-heading-fixed');
        } else {
            processing_steps.removeClass('top-fixed animate__fadeInDown');
            changeForm_title.removeClass('steps-heading-fixed');
        }

    });

    // Gender selection
    $('.gender-select').find('.dropdown-menu').find('li').each(function(){
        dropdownSelect($(this), $('.gender-select'));
        $(this).find('.dropdown-item').on('click', function(){    
            $('.gender-select').find('.dropdown-toggle').addClass('selected-moment');
        });
    });
    // Country selection
    $('.country-select').find('.dropdown-menu').find('li').each(function(){
        dropdownSelect($(this), $('.country-select'));
        $(this).find('.dropdown-item').on('click', function(){
            $('.country-select').find('.dropdown-toggle').addClass('selected-moment');
        });
    });
    // Question selection
    $('.question-select').find('.dropdown-menu').find('li').each(function(){
        dropdownSelect($(this), $('.question-select'));
        $(this).find('.dropdown-item').on('click', function(){
            $('.question-select').find('.dropdown-toggle').addClass('selected-moment');
        });
    });

    // prev button enable 
    function prevBtn_enabled() {
        $('#prv-stp-btn').removeClass('disabled');
        $('#prv-stp-btn').addClass('animate__animated animate__fadeIn');
    }

    // prev button disable
    function prevBtn_disabled() {
        $('#prv-stp-btn').addClass('disabled');
        $('#prv-stp-btn').removeClass('animate__animated animate__fadeIn');
    }

    // step heading title
    var step_one_title = 'Getting started';
    var step_two_title = 'Contact Details';
    var step_three_title = 'Security Details';
    var step_four_title = 'Yeah! It’s Almost Done';

    var heading_title = $('.poklotto-form').find('.steps-heading-title');
    
    // step processing
    var step_1 = $('.processing-steps').find('.first-step');
    var step_2 = $('.processing-steps').find('.second-step');
    var step_3 = $('.processing-steps').find('.third-step');
    var step_4 = $('.processing-steps').find('.last-step');

    function step_processing_change(thisStepProcess) {
        if(thisStepProcess.next().hasClass('second-step-form')) {
            step_2.addClass('current-step');
            step_2.prev().addClass('current-arrow');
        } else if(thisStepProcess.next().hasClass('third-step-form')) {
            step_3.addClass('current-step');
            step_3.prev().addClass('current-arrow');
        } else if(thisStepProcess.next().hasClass('fourth-step-form')) {
            step_4.addClass('current-step');
            step_4.prev().addClass('current-arrow');
        }
    }
    function step_processing_change2(thisStepProcess) {
        if(thisStepProcess.prev().hasClass('first-step-form')) {
            step_2.removeClass('current-step');
            step_2.prev().removeClass('current-arrow');
        } else if(thisStepProcess.prev().hasClass('second-step-form')) {
            step_3.removeClass('current-step');
            step_3.prev().removeClass('current-arrow');
        } else if(thisStepProcess.prev().hasClass('third-step-form')) {
            step_4.removeClass('current-step');
            step_4.prev().removeClass('current-arrow');
        }
    }

    // step heading title change
    function stepTitle_change(thisStepHeading){
        if(thisStepHeading.next().hasClass('first-step-form')) {
            heading_title.text(step_one_title);
        } else if(thisStepHeading.next().hasClass('second-step-form')) {
            heading_title.text(step_two_title);
        } else if(thisStepHeading.next().hasClass('third-step-form')) {
            heading_title.text(step_three_title);
        } else if(thisStepHeading.next().hasClass('fourth-step-form')) {
            heading_title.text(step_four_title);
        }
    }
    function stepTitle_change2(thisStepHeading){
        if(thisStepHeading.prev().hasClass('first-step-form')) {
            heading_title.text(step_one_title);
        } else if(thisStepHeading.prev().hasClass('second-step-form')) {
            heading_title.text(step_two_title);
        } else if(thisStepHeading.prev().hasClass('third-step-form')) {
            heading_title.text(step_three_title);
        } else if(thisStepHeading.prev().hasClass('fourth-step-form')) {
            heading_title.text(step_four_title);
        }
    }

    // step heading title animate
    function heading_title_animated() {
        heading_title.addClass('animated');
        setTimeout(function() {
            heading_title.removeClass('animated');
        },600);
    }

    var prevIsClicked;
    prevIsClicked = false;
    $('#nxt-stp-btn').on('click', function(e){
        e.preventDefault(e);
        $('.form-all-step').find('.per-step.blanked').each(function(){
            var nextEl = $(this).next().hasClass('per-step');
            nextEl == true;

            if(nextEl == true) {
                $(this).next().addClass('blanked');
                $(this).removeClass('blanked');
                $(this).addClass('completed');

                // animate
                $(this).addClass('animate__fadeOutLeft');
                $(this).next().addClass('animate__fadeInRight');
                $(this).removeClass('animate__fadeInRight');
                $(this).next().removeClass('animate__fadeOutRight');

                if(prevIsClicked == true) {
                    prevIsClicked = false;
                }
                if(prevIsClicked ==  false) {
                    $(this).css('position', 'absolute');
                    $(this).next().css('position', 'relative');
                }

                stepTitle_change($(this));
                heading_title_animated();
                step_processing_change($(this));
            }
        });
        prevBtn_enabled();
    });
    
    $('#prv-stp-btn').on('click', function(e){
        e.preventDefault(e);
        $('.form-all-step').find('.per-step.blanked').each(function(){
            var prevEl = $(this).prev().hasClass('per-step');
            var firstStepEL = $(this).prev().hasClass('first-step-form');
            prevEl == true;
            firstStepEL == false;

            if(prevEl == true) {
                $(this).prev().removeClass('completed');
                $(this).prev().addClass('blanked');
                $(this).removeClass('blanked');

                // animate
                $(this).removeClass('animate__fadeInRight');
                $(this).prev().removeClass('animate__fadeOutLeft');
                $(this).addClass('animate__fadeOutRight');
                $(this).prev().addClass('animate__fadeInLeft');

                if(prevIsClicked == false) {
                    prevIsClicked = true;
                }

                if(prevIsClicked == true) {
                    $(this).css('position', 'absolute');
                    $(this).prev().css('position', 'relative');
                }
                stepTitle_change2($(this));
                heading_title_animated();
                step_processing_change2($(this));
            }


            if(firstStepEL == true) {
                prevBtn_disabled();
            }
            
        });
    });

    $('#big-screen').on('click', function(e){
        e.preventDefault();
        $('.sign-up').toggleClass('fixed-screen').stop();

        if($('#big-screen').find('.fa-solid').hasClass('fa-expand')) {
            $('#big-screen').find('.fa-solid').removeClass('fa-expand');
            $('#big-screen').find('.fa-solid').addClass('fa-compress');
        } else {
            $('#big-screen').find('.fa-solid').addClass('fa-expand');
            $('#big-screen').find('.fa-solid').removeClass('fa-compress');
        }
    });
});