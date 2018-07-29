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

    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
    });
});

function cloneMore(selector, type) {
    let newElement = $(selector).clone(true);
    let total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
        let name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        let id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        let newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}