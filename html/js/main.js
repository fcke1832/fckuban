$(document).ready(function(){
  var gd = $('.game-date');

	$('.main-slider').slick({
	  dots: true,
	  speed: 500,
	  fade: true,
	  cssEase: 'linear',
	  autoplay: true,
  	  autoplaySpeed: 1000
	});


  $('.calendar-info').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    asNavFor: '.calendar-nav',
    draggable: false
  });
  $('.calendar-nav').slick({
    slidesToShow: 5,
    slidesToScroll: 1,
    asNavFor: '.calendar-info',
    dots: false,
    centerMode: true,
    arrows: false,
    focusOnSelect: true,
    infinite: false,
    variableWidth: true,
    draggable:false
   });
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




 
