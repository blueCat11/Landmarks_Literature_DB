$(document).ready( function() {
    handleVisualizeDeletion("purpose");
    handleVisualizeDeletion("core_attribute");
    handleVisualizeDeletion("link");
    //DONE (see addFormToFormsetDynamically.js:
    // when a clear-checkbox looses focus (blur) check whether it is set or not and adjust color accordingly

});

function handleVisualizeDeletion(type_of_form){
    let form_related_class = type_of_form + "_related";
    let form_class = type_of_form + "_form";
    let delete_id_part = "delete_this_" + type_of_form;

    let form_related_stuff = document.getElementsByClassName(form_related_class)[0];
    let single_forms = form_related_stuff.getElementsByClassName(form_class);
    for (let index = 0; index<single_forms.length; ++index){
        let form = single_forms[index];
        let delete_els = form.querySelectorAll("[id*='"+delete_id_part+"'");
        for (let j = 0; j < delete_els.length; ++j ){
            let delete_el = delete_els[j];
            //console.log(delete_el);
            delete_el.onchange = function() {setVisualizeDeletion(this, type_of_form)};
            if(delete_el.checked){
                single_forms[index].classList.add("not_saved"); //turn background red
            }else{
                single_forms[index].classList.remove("not_saved") //delete red class, make background default again
            }
        }
    }
}


function setVisualizeDeletion(element, type_of_form){
    let form_class = type_of_form + "_form";
    console.log(element);
    let id = element.id;
    if(element.checked){
        $("#"+id).parents( "."+form_class ).addClass( "not_saved" );
        //single_forms[index].classList.add("not_saved"); //turn background red
    }else{
        $("#"+id).parents("."+form_class).removeClass("not_saved");
          //      single_forms[index].classList.remove("not_saved") //delete red class, make background default again
    }
}
/*
function setVisualizeDeletion(id_of_input, id_of_parent){
    if ($("#"+id_of_input).checked){
        document.getElementById(id_of_parent).classList.add("not_saved")
    }else{
        document.getElementById(id_of_parent).classList.remove("not_saved")
    }
}
*/
