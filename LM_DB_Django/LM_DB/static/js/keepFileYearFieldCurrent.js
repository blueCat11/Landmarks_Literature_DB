$(document).ready( function() {
    let $paperYearField = $("#id_paper-year");
    let $fileYearField = $("#id_file-year");
    updateFileYearField($paperYearField, $fileYearField);
    $paperYearField.change( function(event) {
        updateFileYearField($paperYearField, $fileYearField)
    });

});

function updateFileYearField($paperYearField, $fileYearField){
    $fileYearField.val($paperYearField.val());
}