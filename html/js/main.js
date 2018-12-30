
$(document).ready(function(){
  var gamedate = $("div.calendar-nav").find("div.slick-slide").children();
  var win = $(this);

$('.publication-p').each(function(index, element) {
    $clamp(element, { clamp: 5});
});

var timer = new Timer();
$('#chronometre .startButton').click(function () {
    timer.start();
});
$('#chronometre .pauseButton').click(function () {
    timer.pause();
});
$('#chronometre .stopButton').click(function () {
    timer.stop();
});
$('#chronometre .resetButton').click(function () {
    timer.reset();
});
timer.addEventListener('secondsUpdated', function (e) {
    $('#chronometre .values').html(timer.getTimeValues().toString());
});
timer.addEventListener('started', function (e) {
    $('#chronometre .values').html(timer.getTimeValues().toString());
});
timer.addEventListener('reset', function (e) {
    $('#chronometre .values').html(timer.getTimeValues().toString());
});
// scotetable table height
 if ($(this).width() <= 955) {
  $('.scrollbar').css('height' , '100%');
};
if ($(this).width() >= 956) {
  $('.scrollbar').height($('.scoretable').height() - 50 - $('.team-select').height());
};
 // scrollbar height on wide screen
if ($(this).width() >= 2560){
$('.scrollbar').height($('.scoretable') - 70 - $('.team-select').height());
};
// sript for Header Menu and scoretable on resize
window.addEventListener("resize", function() {
  if ($(this).width() >= 956) {
  $(".header-menu").css('display' , 'block');
  $('.scoretable-items').css("display", "block");
  $('.scrollbar').height($('.scoretable').height() - 50 - $('.team-select').height());
 }else {
  $('.header-menu').css('display' , 'none'); 
<<<<<<< HEAD
=======
  $('.scoretable-items').css("display", "none");
>>>>>>> 417fcc368c4781cb69f056a12c8a9589943a4633
}
});
// sript  scrollbar on resize
window.addEventListener("resize", function() {
  if ($(this).width() >= 2560) {
  $('.scrollbar').height($('.scoretable').height() - 70 - $('.team-select').height());
 }else {
  $('.scrollbar').height($('.scoretable').height() - 50 - $('.team-select').height());
}
});
window.addEventListener("resize", function() {
  if ($(this).width() <= 955) {
   $('.scrollbar').css('height' , '100%');
 }else {
  $('.scrollbar').height($('.scoretable').height() - 50 - $('.team-select').height());
}
});
// sript for Scoretable on resize
$('.scoretable-trigger').on("click", function() {
  if (win.width() <= 956) {
    $('.scoretable-items').slideToggle();       
  };
});
$(window).on('orientationchange', function() {
  $('.scoretable-items').css("display", "");
});
// Insagram widget
var galleryFeed = new Instafeed({
  get: "user",
  userId: 4622774,
  accessToken: "4622774.7cbaeb5.ec8c5041b92b44ada03e4a4a9153bc54",
  resolution: "thumbnail",
  useHttp: "true",
  limit: 9,
  template: '<div class="img-wrap"><a href="{{link}}"><div class="img-featured-container"><div class="img-backdrop"></div><div class="description-container"><i class="icon ion-heart"></i><span class="likes">{{likes}}</span><i class="icon icon-chatbubble"></i><span class="comments">{{comments}}</span></div><img src="{{image}}" class="img-responsive"></div></a></div>',
  target: "instafeed-gallery-feed",
});
galleryFeed.run();

// sliders
$('.main-slider').slick({
 dots: true,
 speed: 500,
 fade: true,
 cssEase: 'linear',
 // autoplay: true,
 autoplaySpeed: 3000,
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
var SlidesCount = $('.day').closest('span').length - 1;
var Initial = $('#current-slide').index();
<<<<<<< HEAD
=======

>>>>>>> 417fcc368c4781cb69f056a12c8a9589943a4633
  $('.calendar-nav').slick({
    slidesToShow: SlidesCount,
    slidesToScroll: 1,
    asNavFor: '.calendar-info',
    dots: false,
    centerMode: true,
    centerPadding: '0px',
    arrows: false,
    focusOnSelect: true,
    infinite: false,
    initialSlide: Initial,
    variableWidth: true,
    draggable:false,
    swipe: false
  });
    $('.calendar-info').slick({
    infinite: false,
    dots: false,
    arrows: false, 
    slidesToShow: 1,
    slidesToScroll: 1,
<<<<<<< HEAD
=======
    arrows: false,
>>>>>>> 417fcc368c4781cb69f056a12c8a9589943a4633
    asNavFor: '.calendar-nav',
    draggable: false,
    swipe: false,
    initialSlide: Initial,
  });
<<<<<<< HEAD
        $('.open-publication-slider').slick({
    infinite: true,
    dots: true,
    arrows: true, 
    slidesToShow: 1,
    slidesToScroll: 1,
  });
=======
>>>>>>> 417fcc368c4781cb69f056a12c8a9589943a4633
// header menu and searchfield slide
$('.menu-icon').on('click',function() {
 $(".header-menu").slideToggle();
});
$('.search').on('click',function() {
 $(".search-field").slideToggle();
});
$('.team-button').on('click',function() {
  $('.team-button').not(this).removeClass('active-button');
  $(this).addClass('active-button');
});
// size for calendar navigation items
$('div.calendar-nav').find("div.slick-slide").children().addClass('game-date').width($('.calendar-nav').width() * 0.17);
$('div.slick-current').find("div.game-date").addClass('current').width($('.calendar-nav').width() * 0.32);
$('.game-date').on('click', function() {
  $('.game-date').not(this).removeClass('current').width($('.calendar-nav').width() * 0.17);
  $(this).addClass('current').width($('.calendar-nav').width() * 0.32);
});
$( window ).on("resize", function(){
   $('.game-date').width($('.calendar-nav').width() * 0.17);
  $('div.slick-current').find("div.game-date").width($('.calendar-nav').width() * 0.32);
});  
});



