$(document).ready( function() {
    //addLabelClass();
    addListClass();
    addFormControlsClass();
});

function addListClass(){
    $('#id_paper_keywords-paper_keywords').addClass('uk-list');
    $('#id_concept_name-paper_concept_name').addClass('uk-list');
    $('#id_paper_categories-paper_categories').addClass('uk-list');
    $('#id_new_category-super_category').addClass('uk-list');
}

function addFormControlsClass(){
    let $inputs = $('#lm_data_form').find(':input');
    let index;
    //$inputs.wrap( "<div class='.uk-form-controls'></div>" );
    for (index = 0; index < $inputs.length; ++index){
        let $current_input = $inputs[index];
        let current_type = $current_input.type;
        let $current_label = $("label[for='"+$current_input.id+"']");
        switch(current_type) {
            case "textarea":
                $current_label.addClass("uk-form-label width_small");
                $current_input.classList.add("uk-textarea");
                $current_input.classList.add("uk-form-controls");
                $current_input.classList.add("uk-form-width-large");
                $current_input.classList.add("uk-form-small");
                //$current_input.wrap("<div class='.uk-form-controls'></div>");
                break;
            case "text":
                $current_label.addClass("uk-form-label width_small");
                $current_input.classList.add("uk-input");
                $current_input.classList.add("uk-form-controls");
                $current_input.classList.add("uk-form-width-large");
                //$current_input.wrap("<div class='.uk-form-controls'></div>");
                break;
            case "file":
                $current_label.addClass("uk-form-label width_small");
                $current_input.classList.add("uk-form-controls");
                //$current_input.wrap("<div class='.uk-form-controls'></div>");

                break;
            case "checkbox":
                $current_input.classList.add("uk-checkbox");
                if ($current_input.id !== "file-complete_file_path-clear_id"){
                    $current_label.wrap("<div class='.uk-form-controls uk-form-controls-text'></div>"); // makes clear text be next to checkbox
                }
                break;
            case "button":
                //stuff already there
                break;
            case "radio":
                $current_label.addClass("keep_left");
                $current_input.classList.add("uk-radio");
                $current_label.wrap("<div class='.uk-form-controls uk-form-controls-text'></div>");
                break;
            case "number":
                $current_label.addClass("uk-form-label width_small");
                $current_input.classList.add("uk-form-controls");
                break;
            default:


        }

    }


}
