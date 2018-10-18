$(document).ready( function() {
    addLabelClass();
    addFormControlsClass();
});

function addLabelClass(){
    let labels = document.getElementsByTagName('label');
    let index;

    for (index = 0; index < labels.length; ++index) {
        labels[index].className += "uk-form-label width_small"
    }
}

function addFormControlsClass(){
    let inputs = $('#lm_data_form').find(':input');
    let index;
    $('#lm_data_form').find(':input').wrap( "<div class='.uk-form-controls'></div>" );
    for (index = 0; index < inputs.length; ++index){
        let current_input = inputs[index];
        //current_input.$.wrap( "<div class='.uk-form-controls'></div>" );
        let current_type = current_input.type;
        switch(current_type) {
            case "textarea":
                current_input.className += " .uk-textarea";
                break;
            case "text":
                current_input.className += " .uk-input";
                break;
            case "file":

                break;
            case "checkbox":
                current_input.className += " .uk-checkbox";
                break;
            case "button":
                current_input.className += " uk-button uk-button-default";
                break;
            case "radio":
                current_input.className += " .uk-checkbox";
                break;
            default:

        }
        console.log(index)
        console.log(inputs[index].id)
        console.log(inputs[index].type)
    }
    //TODO iterate over all inputs in form and add a form control div around them

}