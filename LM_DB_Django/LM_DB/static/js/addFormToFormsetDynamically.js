//https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
// cloneMore accepts selector as the first argument, and the type of formset as the 2nd one.
// What the selector should do is pass it what it should duplicate.
// In this case, I pass it div.table:last so that jQuery looks for the last table with a class of table.
// The :last part of it is important because the selector is also used to determine what the new form will be inserted after.
// More than likely you'd want it at the end of the rest of the forms.
// The type argument is so that we can update the management_form field, notably TOTAL_FORMS, as well as the actual form fields.
// If you have a formset full of, say, Client models,
// the management fields will have IDs of id_clients-TOTAL_FORMS and id_clients-INITIAL_FORMS,
// while the form fields will be in a format of id_clients-N-fieldname with N being the form number, starting with 0.
// So with the type argument the cloneMore function looks at how many forms there currently are, and goes through every
// input and label inside the new form replacing all the field names/ids from something like id_clients-(N)-name to id_clients-(N+1)-name and so on.
// After it is finished, it updates the TOTAL_FORMS field to reflect the new form and adds it to the end of the set.

$(document).ready( function() {

    $("#add_core_attribute").click( function(event) {
        checkIfNeedsClone('div.core_attribute_form:last', 'core_attribute');
    });

    $("#add_link").click( function(event) {
        checkIfNeedsClone('div.link_form:last', 'link');
    });

    $("#add_purpose").click( function(event) {
        checkIfNeedsClone('div.purpose_form:last', 'purpose');
    });

    $("#add_author").click( function(event) {
        checkIfNeedsClone('div.author_form:last', 'author');
    });

});

function checkIfNeedsClone(selector, type){
    if ($(selector).hasClass("hidden")){
        $(selector).removeClass("hidden");
    }else{
        cloneMore(selector, type);
    }
}

function setVisualizeDeletion(element, type_of_form){
    let form_class = type_of_form + "_form";
    let id = element.id;
    if(element.checked){
        $("#"+id).parents( "."+form_class ).addClass( "not_saved" );
    }else{
        $("#"+id).parents("."+form_class).removeClass("not_saved");
    }
}

function cloneMore(selector, type) {
    let newElement = $(selector).clone(true);
    newElement.removeClass('not_saved');
    let total = $('#id_' + type + '-TOTAL_FORMS').val();
    let delete_id = "";
    newElement.find(':input').each(function() {
        let name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        let id = 'id_' + name;
        let id_str = String(id);
        if ($(this).attr('type')==="button"){
             $(this).attr({'name': name, 'id': id});
        }else {
            $(this).attr({'name': name, 'id': id}).val(''); //.removeAttr('checked');
            // $(this).prop( "checked", false ); // possibly  instead add this

            if (id_str.includes('delete_this')){
                $(this).attr({'name': name, 'id': id});
                $(this).removeAttr("value"); // original checkbox doesn't have value-Attribute, and for some reason, this seems to confound the deletion process if left in
                $(this).prop( "checked", false );
                delete_id = id_str;
                console.log(id_str);
            }else{
                $(this).attr({'name': name, 'id': id}).val('');
            }
        }

    });
    newElement.find('label').each(function() {
        let newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    document.getElementById(delete_id).onchange = function(){setVisualizeDeletion(this, type)};

}

// delete (or hide) the selected form from view
// should delete values in form in any case (but doesn't yet)
// this function is currently not in use, too complicated consequences:
// // The form-counts would have to be updated, too
// // + the numbering of all the forms in the formset would need to be adjusted, so that there's no number higher than the total form-count

// If you want to use delete buttons, add this or similar (change name, id...) into the html after each form
//<input type="button" value="Delete" name="delete_core_attribute-{{ forloop.counter0 }}" id="delete_core_attribute-{{ forloop.counter0 }}" onclick="delete_form(this)">


function delete_form(element){
    let form = element.parentElement;
    let parent_of_form = form.parentElement;
    if ($(parent_of_form.children("div.single_form").length()) <= 1){
        form.classList.add("hidden");
        form.find(':input').each(function() {
        let name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        let id = 'id_' + name;
        if ($(this).attr('type')==="button"){
             $(this).attr({'name': name, 'id': id});
        }else {
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        }
    });

    }else {
        parent_of_form.removeChild(form);
    }
}