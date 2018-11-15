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
