if ($(".tf-sw-card").length > 0) {
  var swiper = new Swiper(".tf-sw-card", {
    autoplay: {
      delay: 200,
      disableOnInteraction: false,
      pauseOnMouseEnter: true,
    },
    observer: true,
    observeParents: true,
    autoplay: true,
    slidesPerView: 4,
    loop: true,
    spaceBetween: 24,
    speed: 600,
    breakpoints: {
      0: {
        slidesPerView: 1
      },
      500: {
        slidesPerView: 2
      },
      768: {
        slidesPerView: 4
      }
    },
  });

}

