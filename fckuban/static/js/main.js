
$(document).ready(function(){
  var gamedate = $("div.calendar-nav").find("div.slick-slide").children();
  var win = $(this);
  // замена лишних строк на троеточие в плитке новостей
  $(".publication-p").each(function(index, element) {
    $clamp(element, { clamp: 5});
  });
  // таймер на странице онлайн-трансляций
  var timer = new Timer();
  $("#chronometre .startButton").click(function () {
    timer.start();
  });
  $("#chronometre .pauseButton").click(function () {
    timer.pause();
  });
  $("#chronometre .stopButton").click(function () {
    timer.stop();
  });
  $("#chronometre .resetButton").click(function () {
    timer.reset();
  });
  timer.addEventListener("secondsUpdated", function (e) {
    $("#chronometre .values").html(timer.getTimeValues().toString());
  });
  timer.addEventListener("started", function (e) {
    $("#chronometre .values").html(timer.getTimeValues().toString());
  });
  timer.addEventListener("reset", function (e) {
    $("#chronometre .values").html(timer.getTimeValues().toString());
  });
  // высота турнирной таблицы на разных экранах
  if ($(this).width() <= 955) {
    $(".scrollbar").css("height" , "100%");
  };
  if ($(this).width() >= 956) {
    $(".scrollbar").height($(".scoretable").height() - 50 - $(".team-select").height());
  };
  if ($(this).width() >= 2560){
    $(".scrollbar").height($(".scoretable") - 70 - $(".team-select").height());
  };
  window.addEventListener("resize", function() {
    if ($(this).width() >= 2560) {
      $(".scrollbar").height($(".scoretable").height() - 70 - $(".team-select").height());
    }else {
      $(".scrollbar").height($(".scoretable").height() - 50 - $(".team-select").height());
    }
  });
  window.addEventListener("resize", function() {
    if ($(this).width() <= 955) {
     $(".scrollbar").css("height" , "100%");
   }else {
    $(".scrollbar").height($(".scoretable").height() - 50 - $(".team-select").height());
  }
});
  // анимация стрелки в строке турнирной таблицы на мал. экранах
  $(".team").append("<a href='javascript:;' class='team-logo-link'>");
  $(".team-logo-link").on("click",function() {
    $(this).toggleClass("rotate-link");
    $(this).parent().siblings("td:nth-child(n + 3)").toggleClass("slide");
  });
  // Сворачивание главного меню нв маленьком экране
  window.addEventListener("resize", function() {
    if ($(this).width() >= 956) {
      $(".header-menu").css("display" , "block");
      $(".scoretable-items").css("display", "block");
      $(".scrollbar").height($(".scoretable").height() - 50 - $(".team-select").height());
    }else {
      $(".header-menu").css("display" , "none"); 
    }
  });
  // слайд турнирной таблицы на маленьких экранах
  $(".scoretable-trigger").on("click", function() {
    if (win.width() <= 956) {
      $(".scoretable-items").slideToggle();       
    };
  });
  $(window).on("orientationchange", function() {
    $(".scoretable-items").css("display", "");
  });
  // слайдеры
  $(".main-slider").slick({
   dots: true,
   speed: 500,
   fade: true,
   cssEase: "linear",
   autoplay: true,
   autoplaySpeed: 7000,
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
  var SlidesCount = $(".day").closest("span").length - 1;
  var Initial = $("#current-slide").index();
  $(".calendar-nav").slick({
    slidesToShow: SlidesCount,
    slidesToScroll: 1,
    asNavFor: ".calendar-info",
    dots: false,
    centerMode: true,
    centerPadding: "0px",
    arrows: false,
    focusOnSelect: true,
    infinite: false,
    initialSlide: Initial,
    variableWidth: true,
    draggable:false,
    swipe: false
  });
  $(".calendar-info").slick({
    infinite: false,
    dots: false,
    arrows: false, 
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    asNavFor: ".calendar-nav",
    draggable: false,
    swipe: false,
    initialSlide: Initial,
  });
  $(".other-players").on("click",function() {
   $(".other-players-slider").slideToggle();
 });
  $(".other-players-slider").slick({
    infinite: true,
    dots: false,
    arrows: true, 
    slidesToShow: 5,
    slidesToScroll: 1,
  });
  $(".open-publication-slider").slick({
    infinite: true,
    dots: true,
    arrows: true, 
    slidesToShow: 1,
    slidesToScroll: 1,
  });
  var PublicationSlidesLenght = $(".open-publication-slider").find($("li")).length
  if (PublicationSlidesLenght > 9) {
    $(".open-publication-slider").addClass("margin-for-dots");
  }
  //выпадающее фото в слайдере на странице новости
  $(".popup").click(function(){
    var img = $(this);
    var src = img.attr('src');
    $("body").append("<div class='popup-wrap'>"+ 
     "<div class='popup-bg'>"+ 
     "<img src='"+src+"' class='popup-img'/>"+ 
     "</div>"+
     "</div>"); 
    $(".popup-wrap").fadeIn(800); 
    $(".popup-bg").click(function(){    
      $(".popup-wrap").fadeOut(800); 
      setTimeout(function() { 
        $(".popup-wrap").remove(); 
      }, 800);
    });
  });
  // слайд меню и поиска на маленьких экранах
  $(".menu-icon").on("click",function() {
   $(".header-menu").slideToggle();
 });
  $(".search").on("click",function() {
   $(".search-field").slideToggle();
 });
  // стиль кнопки комманды в турнирной таблице
  $(".team-button").on("click",function() {
    $(".team-button").not(this).removeClass("active-button");
    $(this).addClass("active-button");
  });
  // ширина элементов навигации в календаре
  $("div.calendar-nav").find("div.slick-slide").children().addClass("game-date").width($(".calendar-nav").width() * 0.17);
  $("div.slick-current").find("div.game-date").addClass("current").width($(".calendar-nav").width() * 0.32);
  $(".game-date").on("click", function() {
    $(".game-date").not(this).removeClass("current").width($(".calendar-nav").width() * 0.17);
    $(this).addClass("current").width($(".calendar-nav").width() * 0.32);
  });
  $( window ).on("resize", function(){
   $(".game-date").width($(".calendar-nav").width() * 0.17);
   $("div.slick-current").find("div.game-date").width($(".calendar-nav").width() * 0.32);
 });  
});



