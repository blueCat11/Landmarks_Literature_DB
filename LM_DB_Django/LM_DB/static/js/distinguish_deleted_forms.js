$(document).ready( function() {
    setVisualizeDeletion("id_purpose-0-delete_this_purpose", "purpose_form" );

    //TODO: color forms red, where cleared attribute is set
    //TODO: when a clear-checkbox looses focus (blur) check whether it is set or not and adjust color accordingly

});


$

function setVisualizeDeletion(id_of_input, id_of_parent){
    if ($("#"+id_of_input).checked){
        document.getElementById(id_of_parent).classList.add("not_saved")
    }else{
        document.getElementById(id_of_parent).classList.remove("not_saved")
    }
}