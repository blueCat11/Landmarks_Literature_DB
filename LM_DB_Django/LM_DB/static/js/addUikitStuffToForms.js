$(document).ready( function() {
    addLabelClass();
});

function addLabelClass(){
    let labels = document.getElementsByTagName('label');
    let index;

    for (index = 0; index < labels.length; ++index) {
        labels[index].className += "uk-form-label"
    }
}

function addFormControlsClass(){
    //TODO iterate over all inputs in form and add a form control div around them

}