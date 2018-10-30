function toggleVisibility(currentButtonId, selectorToBeToggled){
    $(selectorToBeToggled).toggle();
    let $currentButton = $('#'+currentButtonId);
    console.log($currentButton);
    let currentIcon = $currentButton.attr("uk-icon");
    console.log(currentIcon);
    if (currentIcon === "chevron-down"){
        $currentButton.attr("uk-icon", "chevron-up");
    }else if(currentIcon === "chevron-up"){
        $currentButton.attr("uk-icon", "chevron-down");
    }
}