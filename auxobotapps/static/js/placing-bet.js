// placing a bet
(function ($) {
    "use strict";
    $(document).ready(function($){

        // global variable
        var betRatio;
        var teamName;
        var teamOneName;
        var teamTwoName;
        var teamOneLogo;
        var teamTwoLogo;
        var teamOneScore;
        var teamTwoScore;
        var stakeDG;
        var bettotal;
        var matchID;
        var updateplacedID;
        var for_upadte_stake;
        var modalOpenFromPage = true;

        // ------------------------------------------------------
        // step #02 : popup modal
        // ------------------------------------------------------

        // append BS5 modal to body
        var modalElement = `
            <div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="placing-bet-modal">
                        <div class="pb-modal-header">
                            <span class="modal-title">Place your bet</span>
                            <button class="prd-close-btn" data-bs-dismiss="modal"><i class="fa-light fa-xmark"></i></button>
                        </div>
                        <div class="pb-modal-body">
                            <div class="selected-team">
                                <span class="slct-team-name">Dinamo Zagreb</span>
                                <span class="slct-bet-ratio"></span>
                            </div>
                            <div class="selected-match">
                                <div class="single-team">
                                    <div class="team-icon">
                                        <img src="assets/img/sports-schedule/team-icon/icon-1.png" alt="">
                                    </div>
                                    <span class="team-name">Dinamo Zagreb</span>
                                </div>
                                <img src="assets/img/playing-bet/icon/modal-vs.png" alt="" class="versace-icon">
                                <div class="single-team">
                                    <span class="team-name">Bodo Glimt FC</span>
                                    <div class="team-icon">
                                        <img src="assets/img/sports-schedule/team-icon/icon-5.png" alt="">
                                    </div>
                                </div>
                            </div>
                            <div class="scrores-line">
                                [ <span class="team-a-scr">0</span> : <span class="team-b-scr">0</span> ] 1X2 LIVE PREDICTION
                            </div>
                        </div>
                        <div class="pb-ctrl-stake">
                            <div class="prd-btn-group">
                                <button class="minus ctrl-btn"><i class="fa-solid fa-minus"></i></button>
                                <span class="stake-digit">1</span>
                                <button class="add ctrl-btn"><i class="fa-solid fa-plus"></i></button>
                            </div>
                        </div>
                        <div class="pb-calc">
                            <span class="stake-line">Stake : <span class="stk-num"></span></span>
                            <span class="total-return">Total Est. Returns : <span class="ret-num">1.00</span></span>
                        </div>
                        <div class="pb-modal-footer">
                            <button class="prd-btn-1 medium" data-bs-dismiss="modal" id="keepInSlip">keep it in betslip <i class="fa-duotone fa-arrow-right"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        `
        $('body').append(modalElement);

        // data taken from match sheets
        function dataTakenFromMatchSheet(dataMining) {
            betRatio = dataMining.find("[data-bet-ratio='data-bet-ratio']").text();
            teamName = dataMining.find("[data-team-name='data-team-name']").text();
            teamOneName = dataMining.parents('.single-t-match').find("[data-team-one='data-team-one']").text();
            teamTwoName = dataMining.parents('.single-t-match').find("[data-team-two='data-team-two']").text();
            teamOneLogo = dataMining.parents('.single-t-match').find('.single-team').first().find('.team-icon img').attr('src');
            teamTwoLogo = dataMining.parents('.single-t-match').find('.single-team').last().find('.team-icon img').attr('src');
            teamOneScore = dataMining.parents('.single-t-match').find('.single-team').first().find('.team-score').text();
            teamTwoScore = dataMining.parents('.single-t-match').find('.single-team').last().find('.team-score').text();
        }

        // data set to modal 
        function dataSetToModal() {
            $('.placing-bet-modal').find('.slct-team-name').text(teamName);
            $('.placing-bet-modal').find('.slct-bet-ratio').text(betRatio);
            $('.placing-bet-modal').find('.selected-match .single-team').first().find('.team-name').text(teamOneName);
            $('.placing-bet-modal').find('.selected-match .single-team').last().find('.team-name').text(teamTwoName);
            $('.placing-bet-modal').find('.selected-match .single-team').first().find('.team-icon img').attr('src', teamOneLogo);
            $('.placing-bet-modal').find('.selected-match .single-team').last().find('.team-icon img').attr('src', teamTwoLogo);
            $('.placing-bet-modal').find('.scrores-line').find('.team-a-scr').text(teamOneScore);
            $('.placing-bet-modal').find('.scrores-line').find('.team-b-scr').text(teamTwoScore);
            $('.placing-bet-modal').find('.pb-calc').find('.total-return .ret-num').text(betRatio);
            $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(stakeDG);
        }

        // increase & decrease & equal stake
        stakeDG = 1;

        function est_return() {
            var totalfixed = betRatio * stakeDG;
            bettotal = totalfixed.toFixed(2);
            $('.placing-bet-modal').find('.ret-num').text(bettotal);
        }
        function increaseStake() {
            stakeDG++;
            $('.placing-bet-modal').find('.stake-digit').text(stakeDG);
            $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(stakeDG);
            est_return();
        }
        function decreaseStake() {
            if(stakeDG == 1) {
                stakeDG = 1;
            } else {
                stakeDG--;
                est_return();
            }
            $('.placing-bet-modal').find('.stake-digit').text(stakeDG);
            $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(stakeDG);
        }
        function stakeToEqual() {
            stakeDG = 1;
            $('.placing-bet-modal').find('.stake-digit').text(stakeDG);
            $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(stakeDG);
            $('.placing-bet-modal').find('.ret-num').text(bettotal);
        }

        // increase & decrease initialization
        $('.ctrl-btn.add').on('click', function(){
            increaseStake();
        });
        $('.ctrl-btn.minus').on('click', function(){
            decreaseStake();
        });

        // ------------------------------------------------------
        // step #01 : playing-bet section initialization
        // ------------------------------------------------------

        // by default all 'placed' class removed
        $('.placing-bet').find('.single-bet-place').removeClass('placed');
        
        // unique id Generator
        class Generator {
            constructor() { }
            getId() {
                return this.rand++;
            }
        };
        Generator.prototype.rand =  Math.floor(Math.random() * 26) + Date.now();
        var idGen = new Generator();

         // placing confirm or not
        var myModalEl = $('#exampleModal');
        $(myModalEl).on('show.bs.modal', function (event) {});
         $(myModalEl).on('hidden.bs.modal', function (event) { 
             if($('.placing-bet').find('.single-bet-place.current-clicked-item').hasClass('already-placed')) {
                 $('.placing-bet').find('.single-bet-place.current-clicked-item').removeClass('current-clicked-item already-placed');
             } else {
                 $('.placing-bet').find('.single-bet-place.current-clicked-item').removeClass('placed current-clicked-item');
             }
             stakeToEqual();
             modalOpenFromPage = true;
         });

        

        // add modal attribute to all buttons
        $('.placing-bet').find('.single-bet-place').attr({
            "data-bs-toggle" : "modal",
            "data-bs-target" : "#exampleModal",
        });

        // set attribute to get bet stats data
        $('.placing-bet').find('.single-bet-place').find('.team-name').attr('data-team-name', 'data-team-name');
        $('.placing-bet').find('.single-bet-place').find('.bet-ratio').attr('data-bet-ratio', 'data-bet-ratio');
        $('.single-t-match').each(function(){
            $(this).find('.playing-teams').find('.single-team').first().find('.team-name').attr('data-team-one', 'data-team-one');
            $(this).find('.playing-teams').find('.single-team').filter(':nth-child(2)').find('.team-name').attr('data-team-two', 'data-team-two');
        })

        
        $('body').prepend('<div class="flying-shadow hide"><i class="fa-duotone fa-paper-plane"></i></div>');

        // function will execute when click on single bet place
        $('.placing-bet').find('.single-bet-place').on('click', function(e){
            e.preventDefault();
            dataTakenFromMatchSheet($(this));
            dataSetToModal();
            if(!$(this).hasClass('placed')) {
                $(this).addClass('placed current-clicked-item');
                $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(stakeDG);
            } else {
                $(this).addClass('current-clicked-item already-placed');

                // update/edit function 
                for_upadte_stake = $('[data-match-id="' + $(this).attr('id') + '"]').find('.stake-number');
                var update_betReturn = parseInt(for_upadte_stake.text()) * betRatio;
                var update_betReturnDec = update_betReturn.toFixed(2);
                $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(parseInt(for_upadte_stake.text()));
                $('.placing-bet-modal').find('.pb-calc').find('.total-return .ret-num').text(update_betReturnDec);

                var updatedStakeDG = stakeDG = parseInt(for_upadte_stake.text());
                $('.placing-bet-modal').find('.stake-digit').text(updatedStakeDG);
                updateplacedID = $('.placing-bet').find('.placed.current-clicked-item').attr('id');
            }

            // # flying shadow function :
            // $('body').find('.flying-shadow').remove();

            var $element = $(this);
            var elementTop = $element.offset().top;
            var elementLeft = $element.offset().left;
            var viewportTop = $(window).scrollTop();
            var viewportLeft = $(window).scrollLeft();
            var positionTop = elementTop - viewportTop;
            var positionLeft = elementLeft - viewportLeft;
            // console.log('Element position: (' + positionLeft + ', ' + positionTop + ')');


            $('body').find('.flying-shadow').css({'left' : positionLeft, 'top' : positionTop})
        });

        // ------------------------------------------------------
        // step #03 : bet slip integration
        // ------------------------------------------------------

        
        // bet slip scrollbale

        var mobileAllBScardOpen = false;
        var mobileAllBScardHeight = 0; 
        var mobileAllComboHeight = 0;

        function scrollbaleCardResponsive() {
            if($(window).width() > 1399) {
                if($('.singleBS').parents('.all-bs-card').height() > 475) {
                    $('.singleBS').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.singleBS').parents('.all-bs-card').css('height', '475px');
                } else {
                    $('.singleBS').parents('.all-bs-card').css('height', '475px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 343) {
                    $('.card-combo').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-combo').parents('.all-bs-card').css('height', '343px');
                } else {
                    $('.card-combo').parents('.all-bs-card').css('height', '343px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 343) {
                    $('.card-system').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-system').parents('.all-bs-card').css('height', '343px');
                } else {
                    $('.card-system').parents('.all-bs-card').css('height', '343px');
                }
            } else if($(window).width() > 1199) {
                if($('.singleBS').parents('.all-bs-card').height() > 359) {
                    $('.singleBS').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.singleBS').parents('.all-bs-card').css('height', '359px');
                } else {
                    $('.singleBS').parents('.all-bs-card').css('height', '359px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 227) {
                    $('.card-combo').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-combo').parents('.all-bs-card').css('height', '227px');
                } else {
                    $('.card-combo').parents('.all-bs-card').css('height', '227px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 227) {
                    $('.card-system').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-system').parents('.all-bs-card').css('height', '227px');
                } else {
                    $('.card-system').parents('.all-bs-card').css('height', '227px');
                }
            } else if($(window).width() > 991) {
                if($('.singleBS').parents('.all-bs-card').height() > 319) {
                    $('.singleBS').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.singleBS').parents('.all-bs-card').css('height', '319px');
                } else {
                    $('.singleBS').parents('.all-bs-card').css('height', '319px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 187) {
                    $('.card-combo').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-combo').parents('.all-bs-card').css('height', '187px');
                } else {
                    $('.card-combo').parents('.all-bs-card').css('height', '187px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 187) {
                    $('.card-system').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-system').parents('.all-bs-card').css('height', '187px');
                } else {
                    $('.card-system').parents('.all-bs-card').css('height', '187px');
                }
            } else if($(window).width() > 767 && $(window).width() < 992) {
                if($('.singleBS').parents('.all-bs-card').height() > 314) {
                    $('.singleBS').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.singleBS').parents('.all-bs-card').css('height', '314px');
                } else {
                    $('.singleBS').parents('.all-bs-card').css('height', '314px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 190) {
                    $('.card-combo').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-combo').parents('.all-bs-card').css('height', '190px');
                } else {
                    $('.card-combo').parents('.all-bs-card').css('height', '190px');
                }
                if($('.singleBS').parents('.all-bs-card').height() > 190) {
                    $('.card-system').parents('.all-bs-card').overlayScrollbars({}); 
                    $('.card-system').parents('.all-bs-card').css('height', '190px');
                } else {
                    $('.card-system').parents('.all-bs-card').css('height', '190px');
                }
            } 
            
            else if($(window).width() > 0 && $(window).width() < 768) {
                if($('.singleBS').parents('.all-bs-card').height() > mobileAllBScardHeight) {
                    $('.singleBS').parents('.all-bs-card').overlayScrollbars({}); 
                } else {
                    $('.singleBS').parents('.all-bs-card').css('height', mobileAllBScardHeight);
                }
                if($('.singleBS').parents('.all-bs-card').height() > mobileAllComboHeight) {
                    $('.card-combo').parents('.all-bs-card').overlayScrollbars({}); 
                } 
                if($('.singleBS').parents('.all-bs-card').height() > mobileAllComboHeight) {
                    $('.card-system').parents('.all-bs-card').overlayScrollbars({}); 
                }
            } 
        }


        function bsCardScrollable() {
            var bs_single_length = $('.single-bs-card.singleBS').length;
            var bs_combo_length = $('.single-bs-card.card-combo').length;
            var bs_system_length = $('.single-bs-card.card-system').length;

            scrollbaleCardResponsive();
            $(window).on('resize', function(){
                scrollbaleCardResponsive();
            });
        }

       
        if($(window).width() > 0 && $(window).width() < 768) {
            $('.bet-slip').find('.bet-slip-body').height(($(window).height() / 10) * 8);
        } else {
            $('.bet-slip').find('.bet-slip-body').height('auto');
        }

        $(window).on('resize', function(){
            if($(window).width() > 0 && $(window).width() < 768) {
            $('.bet-slip').find('.bet-slip-body').height(($(window).height() / 10) * 8);
            } else {
                $('.bet-slip').find('.bet-slip-body').height('auto');
            } 
        });
        
        $('#bsCategory-profile').find('.part-slip-header').nextUntil('.sibling-4').addBack().wrapAll('<div class="mobile-wrapper"></div>');
        $('#bsCategory-contact').find('.part-slip-header').nextUntil('.sibling-4').addBack().wrapAll('<div class="mobile-wrapper"></div>');


        $(window).on('resize', function(){
            if($(window).width() < 768) {

                $('.single-bs-card.card-combo').closest('.part-slip-header').css({'height' : 'auto', 'flex' : '1'});
                $('.single-bs-card.card-combo').closest('.mobile-wrapper').css({'display' : 'flex', 'flex-direction' : 'column'});

                $('.single-bs-card.card-system').closest('.part-slip-header').css({'height' : 'auto', 'flex' : '1'});
                $('.single-bs-card.card-system').closest('.mobile-wrapper').css({'display' : 'flex', 'flex-direction' : 'column'});
                
                $('.single-bs-card.singleBS').closest('.all-bs-card').css('height', '100%');
                $('.single-bs-card.card-combo').closest('.part-slip-header').find('.all-bs-card').css('height', '100%');
                $('.single-bs-card.card-system').closest('.part-slip-header').find('.all-bs-card').css('height', '100%');
            } 
        });

        function inPlayAddToSlipCard(liveMatchId, color) {
            $('[data-match-id="' + liveMatchId + '"]').find('.slct-place').find('.bet-ratio').css({
                '-webkit-text-fill-color' : color,
                'font-weight' : '500'
            });
        }

        function inPlayIconAddToSlipCard(liveMatchId) {
            var icon = `<span class="live-icon"><img src="assets/img/playing-bet/bet-slip/live-icon.png" alt=""/></span>`;
            if (!$('[data-match-id="' + liveMatchId + '"]').find('.slct-place').find(".live-icon").length > 0) {
                $('[data-match-id="' + liveMatchId + '"]').find('.slct-place').prepend(icon);
            }
        }

        function newBScardAppend() {
            bettotal = $('.placing-bet-modal').find('.ret-num').text();
            var last_4_number = matchID.slice(-4);
            var match_uniqie_number = 'M' + last_4_number;

            var newBScard = `<div class="single-bs-card singleBS" data-match-id="${matchID}">
                    <div class="bs-card-header">
                        <span class="tournament-name">${match_uniqie_number}. UEFA Champions League</span>
                        <div class="slct-place">
                            <span class="team-name">${teamName}</span>
                            <span class="attherate">@</span>
                            <span class="bet-ratio">${betRatio}</span>
                        </div>
                        <button class="slip-dlt">
                            <i class="fa-light fa-trash-can"></i>
                        </button>
                    </div>
                    <div class="slct-match">
                        <span class="sports-category-icon">
                            <img src="assets/img/playing-bet/bet-slip/sports-icon.png" alt="">
                        </span>
                        <span class="team-1">${teamOneName}</span>
                        vs
                        <span class="team-2">${teamTwoName}</span>
                    </div>
                    <div class="bs-card-footer">
                        <button class="prd-btn-1 medium" data-bs-toggle="modal" data-bs-target="#exampleModal">Stake  :<span class="stake-number">${stakeDG}<span/></button>
                        <div class="return-amount">
                            <span class="text">Return : </span>
                            <span class="number">${bettotal}</span>
                        </div>
                    </div>
                </div>`;

            var newBScombo = `<div class="single-bs-card card-combo" data-match-id="${matchID}">
                    <div class="bs-card-header">
                        <span class="tournament-name">${match_uniqie_number}. UEFA Champions League</span>
                        <div class="slct-place">
                            <span class="team-name">${teamName}</span>
                            <span class="attherate">@</span>
                            <span class="bet-ratio">${betRatio}</span>
                        </div>
                        <button class="slip-dlt">
                            <i class="fa-light fa-trash-can"></i>
                        </button>
                    </div>
                    <div class="slct-match">
                        <span class="sports-category-icon">
                            <img src="assets/img/playing-bet/bet-slip/sports-icon.png" alt="">
                        </span>
                        <span class="team-1">${teamOneName}</span>
                        vs
                        <span class="team-2">${teamTwoName}</span>
                    </div>
                </div>`;

            var newBSsystem = `<div class="single-bs-card card-system" data-match-id="${matchID}">
                    <div class="bs-card-header">
                        <span class="tournament-name">${match_uniqie_number}. UEFA Champions League</span>
                        <div class="slct-place">
                            <span class="team-name">${teamName}</span>
                            <span class="attherate">@</span>
                            <span class="bet-ratio">${betRatio}</span>
                        </div>
                        <button class="slip-dlt">
                            <i class="fa-regular fa-trash-can"></i>
                        </button>
                    </div>
                    <div class="slct-match">
                        <span class="sports-category-icon">
                            <img src="assets/img/playing-bet/bet-slip/sports-icon.png" alt="">
                        </span>
                        <span class="team-1">${teamOneName}</span>
                        vs
                        <span class="team-2">${teamTwoName}</span>
                    </div>
                </div>`;
                
            var markedElementBS = $('.part-slip-header').find('.all-bs-card').find('.single-bs-card.singleBS.hidden').parent();
            var markedElementCombo = $('.part-slip-header').find('.all-bs-card').find('.single-bs-card.card-combo.hidden').parent();
            var markedElementSystem = $('.part-slip-header').find('.all-bs-card').find('.single-bs-card.card-system.hidden').parent();
            $(markedElementBS).prepend(newBScard);
            $(markedElementCombo).prepend(newBScombo);
            $(markedElementSystem).prepend(newBSsystem);
            bsCardScrollable();
        }

        var clicked_place_id;
        var for_upadte_stakeFromSlip;

        var tatalEstReturn;
        var totalStakeNum;
        function totalStakeCount() {
            // total stake
            var bs_single_length = $('.single-bs-card.singleBS').not('.hidden');
            totalStakeNum = 0;
            tatalEstReturn = 0;
            $(bs_single_length).each(function(){
                var z = parseInt($(this).find('.stake-number').text());
                var w = parseFloat($(this).find('.return-amount .number').text());
                totalStakeNum += z;
                tatalEstReturn += w;
            });
            $('.bet-slip-calculation').find('.total-stake').text(totalStakeNum);
            $('.bet-slip-calculation').find('.total-est-return').text(tatalEstReturn.toFixed(2));
        }

        function slipCounter() {
            var bs_single_length = $('.single-bs-card.singleBS').not('.hidden').length;
            $('.bet-slip-header').find('.slip-quantity-badge').text(bs_single_length);
        }

        $('#keepInSlip').on('click', function(){
            if(modalOpenFromPage == true) {
                if(!$('.single-bet-place.current-clicked-item').hasClass('already-placed')) {
                    $('.placing-bet').find('.single-bet-place.current-clicked-item').attr('id', idGen.getId());
                    matchID = $('.placing-bet').find('.single-bet-place.current-clicked-item').attr('id');
                    newBScardAppend();
                    totalStakeCount();
                    displayEmptySlip();
                    $('.successfull-card').hide();
                    slipCounter();
                } else {
                    // update/edit function
                    var updatePlaced_id = $('.placing-bet').find('.placed.current-clicked-item').attr('id');
                    $('[data-match-id="' + updatePlaced_id + '"]').find('.stake-number').text(stakeDG);
                    $('[data-match-id="' + updatePlaced_id + '"]').find('.return-amount > .number').text(bettotal);
                    totalStakeCount();
                    displayEmptySlip();
                    $('.successfull-card').hide();
                }
                if($('.single-bet-place.current-clicked-item').parents('.single-t-match').hasClass('match-in-play')) {
                    inPlayIconAddToSlipCard($('.single-bet-place.current-clicked-item').attr('id'));
                    if($('.single-bet-place.current-clicked-item').hasClass('up')) {
                        inPlayAddToSlipCard($('.single-bet-place.current-clicked-item').attr('id'), '#4D8E53');
                    } else if($('.single-bet-place.current-clicked-item').hasClass('down')) {
                        inPlayAddToSlipCard($('.single-bet-place.current-clicked-item').attr('id'), '#ef6665');
                    } else {
                        return false;
                    }
                }
                $('.placing-bet').find('.placed.current-clicked-item').removeClass('current-clicked-item');
            } else {
                $('[data-match-id="' + clicked_place_id + '"]').find('.stake-number').text(stakeDG);
                $('[data-match-id="' + clicked_place_id + '"]').find('.return-amount > .number').text(bettotal);
                totalStakeCount();
                displayEmptySlip();
                $('.successfull-card').hide();
            }
            cardButtonVisiblity();
            comboPackExec();
            if(comboBtnisOn == true) {
                ComboRatioTotalMultipling();
                comboStakeCounting();
            }
            if(systemBTNisON == true) {
                systemRatioTatalMultply();
                comboStakeCounting();
            }

        
            if(mobileAllBScardOpen == false) {
                mobileAllBScardHeight = $('.singleBS').parents('.all-bs-card').height();
                mobileAllComboHeight = $('.card-combo').parents('.all-bs-card').height();
            }
            mobileAllBScardOpen = true;


            var $element = $('.slip-quantity-badge');
            var elementTop = $element.offset().top;
            var elementLeft = $element.offset().left;
            var viewportTop = $(window).scrollTop();
            var viewportLeft = $(window).scrollLeft();
            var positionTop = elementTop - viewportTop;
            var positionLeft = elementLeft - viewportLeft;
            console.log('Element position: (' + positionLeft + ', ' + positionTop + ')');

            $('body').find('.flying-shadow').removeClass('hide');
            $('body').find('.flying-shadow').css({'left' : positionLeft, 'top' : positionTop});

            setTimeout(function() {
                $('body').find('.flying-shadow').addClass('hide');
            }, 600); 

            setTimeout(function() {
                $('.slip-quantity-badge').addClass('animated');
            }, 600);
            setTimeout(function() {
                $('.slip-quantity-badge').removeClass('animated');
            }, 800);
        });

        var deleting_match_id;


        // #function : when to delete single [bet slip card], all same id's card will be deleted.
        function similarBSCardRemove() {
            var All_BSCard = $('.single-bs-card');
            for(var i=0; i < All_BSCard.length; i++) {
                var allCard_ID = All_BSCard[i].getAttribute('data-match-id');
                if(allCard_ID == deleting_match_id) {
                    var deletingSameAttr = $("[data-match-id=" + deleting_match_id + "]");
                    deletingSameAttr.remove();
                }
            }
        }

        // function : when to delete [bet slip card], placed button will be withdraw from as placed. 
        function placedBTNwithdrawnFromPlaced() {
            var singlePlacedC = $('.single-bet-place.placed');
            for (let i = 0; i < singlePlacedC.length; i++) {
                var element = singlePlacedC[i].id;
                if(deleting_match_id == element) {
                    var placedElementRmv =  document.getElementById(deleting_match_id);
                    placedElementRmv.classList.remove("placed");
                    placedElementRmv.classList.remove("already-placed");
                } 
            }
        }
        
        function displayEmptySlip() {
            $('.empty-card').hide();
            var All_BSCard = $('.single-bs-card.singleBS').not('.hidden').length;
            var singlePlacedC = $('.single-bet-place.placed');
            if(All_BSCard < 1) {
                $('.empty-card').show();
                singlePlacedC.removeClass("placed");
                totalStakeCount();
                $('.successfull-card').hide();
                slipCounter();
            } else {
                $('.empty-card').hide();
            }
        }
        displayEmptySlip();

        $('.successfull-card').hide();
        function displaySuccessBet() {   
            var All_BSCard = $('.single-bs-card.singleBS').not('.hidden').length;
            var singlePlacedC = $('.single-bet-place.placed');
            if(All_BSCard >= 1 ) {
                $('.successfull-card').show();
                singlePlacedC.removeClass("placed");
                $('.single-bs-card').not('.hidden').remove();
                totalStakeCount();
                slipCounter();
            } else {
                $('.successfull-card').hide();
                displayEmptySlip();
            }
        }
        $(document).on('click', '.slip-dlt', function(){
            $(this).parents('.single-bs-card').remove();
            deleting_match_id = $(this).parents('.single-bs-card').attr('data-match-id');
            similarBSCardRemove();
            placedBTNwithdrawnFromPlaced()
            bsCardScrollable();
            totalStakeCount();
            displayEmptySlip();
            slipCounter();
            cardButtonVisiblity();
            comboPackExec();
            ComboRatioTotalMultipling();
            comboStakeCounting();
            if(systemBTNisON == true) {
                systemRatioTatalMultply();
                comboStakeCounting();
            }
        });

        $('.bet-slip-calculation').find('.calc-dlt').on('click', function(){
            console.log('test');
            $('.single-bs-card').not('.hidden').remove();
            displayEmptySlip();
            cardButtonVisiblity();
        });

        $('.bet-slip-calculation').find('.placed-to-dashboard').on('click', function(){
            displaySuccessBet();
        });

        // function : single slip edit stake number to show modal

        $(document).on('click', '.bs-card-footer button[data-bs-toggle="modal"]', function(){
            var modal_match_id = $(this).parents('.single-bs-card').attr('data-match-id');
            var placedSelector = $('.single-bet-place.placed[id="'+ modal_match_id +'"]');
            dataTakenFromMatchSheet(placedSelector);
            dataSetToModal();
            modalOpenFromPage = false;
            clicked_place_id = modal_match_id;

            for_upadte_stakeFromSlip = $('[data-match-id="' + clicked_place_id + '"]').find('.stake-number').text();
            var updatedStakeDG = stakeDG = parseInt(for_upadte_stakeFromSlip);
            $('.placing-bet-modal').find('.stake-digit').text(updatedStakeDG);
            $('.placing-bet-modal').find('.pb-calc').find('.stake-line .stk-num').text(updatedStakeDG);
            var updatedReturnFromSlip = betRatio * updatedStakeDG;

            updatedReturnFromSlip;
            $('.placing-bet-modal').find('.pb-calc').find('.total-return .ret-num').text(updatedReturnFromSlip.toFixed(2));
            
        });


        // total est. return return of combo pack

        var comboBtnisOn = false;
        var systemBTNisON = false;
        var singleCardBtn = $('#bsCat-single-tab');
        var comboCardBtn = $('#bsCat-combo-tab');
        var systemCardBtn = $('#bsCat-system-tab');
        systemCardBtn.css({'pointer-events' : 'none',  'filter' : 'blur(1px)'});
        comboCardBtn.css({'pointer-events' : 'none',  'filter' : 'blur(1px)'});
        
        function cardButtonVisiblity() {
            if($('.single-bs-card.singleBS').not('.hidden').length > 1) {
                comboCardBtn.css({'pointer-events' : 'auto',  'filter' : 'blur(0)'});
            } else {
                comboCardBtn.css({'pointer-events' : 'none',  'filter' : 'blur(1px)'});
            }
            if($('.single-bs-card.singleBS').not('.hidden').length > 2) {
                systemCardBtn.css({'pointer-events' : 'auto',  'filter' : 'blur(0)'});
            } else {
                systemCardBtn.css({'pointer-events' : 'none',  'filter' : 'blur(1px)'});
            }
        }

        var resultNumb = 1;
        $('.inc-dec-bet').find('.result-num').text(resultNumb);
        $('.bet-quantity').find('.inc-dec-bet').find('.inc-btn').on('click', function(e){
            e.preventDefault();
            resultNumb++;
            $('.inc-dec-bet').find('.result-num').text(resultNumb);
            ComboRatioTotalMultipling();
            comboStakeCounting();
            if(systemBTNisON == true) {
                systemRatioTatalMultply();
            }
        });
        $('.bet-quantity').find('.inc-dec-bet').find('.dec-btn').on('click', function(e){
            e.preventDefault();
            resultNumb--;
            if(resultNumb <= 1) {
                resultNumb = 1;
            }
            $('.inc-dec-bet').find('.result-num').text(resultNumb);
            ComboRatioTotalMultipling();
            comboStakeCounting();
            if(systemBTNisON == true) {
                systemRatioTatalMultply();
            }
        });


        var onlyComboRatioTotal;
        function comboPackExec() {
            var allComboCard = $('.all-bs-card').find('.single-bs-card.card-combo').not('.hidden');
            onlyComboRatioTotal = 0;
            allComboCard.each(function(){
                onlyComboRatioTotal += parseFloat($(this).find('.bet-ratio').text());
            });
        }

        function ComboRatioTotalMultipling() {
            var afterMultiplion = onlyComboRatioTotal * resultNumb;
            $('.bet-slip-calculation').find('.total-est-return').text(afterMultiplion.toFixed(2));
        }

        function comboStakeCounting() {
            $('.bet-slip-calculation').find('.total-stake').text(resultNumb);
        }

        singleCardBtn.on('click', function(){
            $('.bet-slip-calculation').find('.total-est-return').text(tatalEstReturn.toFixed(2));
            resultNumb = 1;
            comboBtnisOn = false;
            systemBTNisON = false;
            $('.bet-slip-calculation').find('.total-stake').text(totalStakeNum);
        });
        comboCardBtn.on('click', function(){
            $('.bet-slip-calculation').find('.total-est-return').text(onlyComboRatioTotal.toFixed(2));
            resultNumb = 1;
            $('.inc-dec-bet').find('.result-num').text(resultNumb);
            comboBtnisOn = true;
            systemBTNisON = false;
            comboStakeCounting();
        });
        systemCardBtn.on('click', function(){
            resultNumb = 1;
            $('.inc-dec-bet').find('.result-num').text(resultNumb);
            ComboRatioTotalMultipling();
            comboStakeCounting();
            systemBTNisON = true;
            comboBtnisOn = false;
            systemRatioTatalMultply();
        });
       

        var dataValue = 3;
        function systemRatioTatalMultply() {
            var finalReust = onlyComboRatioTotal * resultNumb * dataValue;
            $('.bet-slip-calculation').find('.total-est-return').text(finalReust.toFixed(2));
        }
        var optionBtnText = $('.system-bet-option').find('.bet-option-btn');
        $('.system-bet-option').find('.dropdown-item').on('click', function(){
            var CurrentBetValue = parseInt($(this).attr('data-bet-add'));
            console.log(CurrentBetValue);
            optionBtnText.text($(this).text());
            dataValue = CurrentBetValue;
            systemRatioTatalMultply();
        });
        

        $('.placing-bet').find('.single-bet-place').on('click', function(){

            if($(window).width() > 767) {
                if($('.bet-slip-header').hasClass('collapsed')) {
                    $('#keepInSlip').attr({
                        "data-bs-toggle" : "collapse",
                        "data-bs-target" : "#collapseBetSlip",
                    });
                } else {
                    $('#keepInSlip').removeAttr("data-bs-toggle data-bs-target");
                }
            }
            
        });

    });
}(jQuery));	