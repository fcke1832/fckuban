$(document).ready(function(){
  var gd = $('.game-date');
  var win = $(this);

// sript for Scoretable
$(window).on('orientationchange', function() {
  $('.scoretable-items').css("display", "");
  if ($(this).width() >= 850) {
   $('.header-menu').css('display' , 'block'); 
 }else {
  $('.header-menu').css('display' , 'none'); 
}
});

$('.scoretable-trigger').on("click", function() {
  if (win.width() <= 1100) {
    $('.scoretable-items').slideToggle();       
  }
});


var galleryFeed = new Instafeed({
  get: "user",
  userId: 4622774,
  accessToken: "4622774.7cbaeb5.ec8c5041b92b44ada03e4a4a9153bc54",
  resolution: "thumbnail",
  useHttp: "true",
  limit: 9,
  template: '<div class="img-wrap"><a href="{{link}}"><div class="img-featured-container"><div class="img-backdrop"></div><div class="description-container"><i class="icon ion-heart"></i><span class="likes">{{likes}}</span><i class="icon icon-chatbubble"></i><span class="comments">{{comments}}</span></div><img src="{{image}}" class="img-responsive"></div></a></div>',
  target: "instafeed-gallery-feed",
  after: function() {
    // disable button if no more results to load
    if (!this.hasNext()) {
      btnInstafeedLoad.setAttribute('disabled', 'disabled');
    }
  },
});
galleryFeed.run();

// sliders
$('.main-slider').slick({
 dots: true,
 speed: 500,
 fade: true,
 cssEase: 'linear',
 autoplay: true,
 autoplaySpeed: 1000,
 responsive: [
 {
  breakpoint: 850,
  settings: {
    arrows: false,
    dots: true
  }
}
]
});


$('.calendar-info').slick({
  slidesToShow: 1,
  slidesToScroll: 1,
  arrows: false,
  asNavFor: '.calendar-nav',
  draggable: false,
  swipe: false
});
$('.calendar-nav').slick({
  slidesToShow: 5,
  slidesToScroll: 1,
  asNavFor: '.calendar-info',
  dots: false,
  centerMode: true,
  centerPadding: 0,
  arrows: false,
  focusOnSelect: true,
  infinite: false,
  variableWidth: true,
  draggable:false,
  swipe: false
});

// header menu and searchfield slide
$('.menu-icon').on('click',function() {
 $(".header-menu").slideToggle();
});
$('.search').on('click',function() {
 $(".search-field").slideToggle();
});

// size for calendar navigation items
gd.width($('.calendar-nav').width() * 0.17);
$('div.slick-current').find("div.game-date").width($('.calendar-nav').width() * 0.32);
gd.on('click', function() {
  gd.not(this).width($('.calendar-nav').width() * 0.17);
  $(this).width($('.calendar-nav').width() * 0.32);
});

$( window ).on("resize", function(){
  gd.width($('.calendar-nav').width() * 0.17);
  $('div.slick-current').find("div.game-date").width($('.calendar-nav').width() * 0.32);
});  
});



