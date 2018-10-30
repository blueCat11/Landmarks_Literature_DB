$(document).ready( function() {
    //pinTableHeader();
});


function pinTableHeader(){
    let window_height = $(window).height();
    let $original_heading = $(".uk-table > thead:nth-child(1)");
    let $heading = $original_heading.clone();

    //$(".uk-table > tbody:nth-child(2)").wrap('<div style="overflow-y:scroll; height:'+window_height+'px;"></div>'); //doesn't work, splits table headings
    $(".double_header").prepend($heading);
    console.log("adjusted");

}

//TODO find a way to optimize this
/*$(function(){
        // Check the initial Poistion of the Sticky Header
        var stickyHeaderTop = $('.uk-table > thead:nth-child(1)').offset().top;

        $(window).scroll(function(){
                if( $(window).scrollTop() > stickyHeaderTop ) {
                        $('.uk-table > thead:nth-child(1)').css({position: 'fixed', top: '0px', background: "white"});
                } else {
                        $('.uk-table > thead:nth-child(1)').css({position: 'static', top: '0px', background: "white"});

                }
        });
  });

  */