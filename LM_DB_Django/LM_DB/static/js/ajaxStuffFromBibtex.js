//Done change to one method fits all: in every case, all possible data should be retrieved from bibtex and entered into appropriate fields
// possible data: title, cite_command, year, author(s), keyword(s)
// add javascript-call to file-upload field
$(document).ready( function() {
    let $file_path_input_field = $("#id_file-complete_file_path");
    $file_path_input_field.click( function(event) {
        sendAjaxToGetInfoFromBibtex("file_upload");
    });
    $file_path_input_field.change( function(event) {
        setOriginalFileName();
    });
});


$(document).ready( function() {
    $("#id_paper-bibtex").blur( function(event) {
        sendAjaxToGetInfoFromBibtex("bibtex_enter");
    });
});


function sendAjaxToGetInfoFromBibtex(context){
    let bibtex = $('#id_paper-bibtex').val();

    let dontSendFlag = $("#id_paper-don_t_overwrite").is(':checked');
    console.log(dontSendFlag);
    if (dontSendFlag) {
        UIkit.notification({
                message: "Fields not updated from Bibtex.",
                status: 'warning',
                pos: 'bottom-center',
                timeout: 2500
            });
    }else {

        $.ajax({
            url : "/LM_DB/enterData/", // the endpoint
            type : "POST", // http method
            data : {
                isYearFromBibtex: true,
                bibtex: bibtex,
                context: context,
            }, // data sent with the post request

            //Done: don't overwrite stuff after first time
            // handle a successful response
            success : function(json) {
                console.log(json.author);
                $('#id_file-year').val(json.year_for_file); // add year into (hidden) field (in file model)
                $('#id_paper-title').val(json.title);
                $('#id_paper-cite_command').val(json.cite_command);
                $('#id_paper-year').val(json.year);
                add_authors(json);
                $('#id_paper-authors').val(json.author);
                $('#id_paper-doi').val(json.doi);
                $('#id_paper-abstract').val(json.abstract);
                let keywords = json.keywords;
                let $keywords_list_in_ui = $("#id_paper_keywords-paper_keywords");
                for (let index = 0; index < keywords.length; ++index){
                    let current_keyword = keywords[index];
                    let $keyword_in_list = $("label").filter(function() {return $.trim($(this).text()) === current_keyword;}).attr('for');
                    if ($keyword_in_list !== undefined && $keyword_in_list !== "") {
                        document.getElementById(String($keyword_in_list)).checked = true
                    }else{
                        //console.log("new Keyword");
                        document.getElementById("id_new_keyword-keyword").value = current_keyword;
                        document.getElementById("id_new_keyword_button").click();
                        // checkmark is always added to newly added elements in ajaxSaveKeyword.js
                    }
                }
                $("#id_paper-don_t_overwrite").prop('checked', true); // assures that bibtex is not by default updated more than once
                if (json.hasOwnProperty('error')){
                    //console.log(json.error);
                    UIkit.notification({
                        message: json.error,
                        status: 'warning',
                        pos: 'bottom-center',
                        timeout: 2500
                    });
                }else{
                   //console.log("success")
                }
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
            });
    }
}


// write values concerning authors to form (and new form)
function add_authors(json){
    let authors = json.author;
    let num_author_forms = $(".author_related").children(".author_form").length;
    for (let i = 0; i < authors.length; ++i){
        let id_part = "id_author-" + i + "-";
        let $current_delete_author_element = $("#" + id_part + "delete_this_author");
        if (num_author_forms < authors.length) {
            if (i > 0){
                $("#add_author").click(); //click on + button
            } else {
                // "delete this" is previously checked for first form, the click unchecks (and triggers the non-red-outline)
                $current_delete_author_element.click()
            }
        }else{
            if ($current_delete_author_element.is(':checked')) {
                $current_delete_author_element.click();
            }
        }
        let author = authors[i];
        $("#"+id_part+"first_name").val(author.first_name);
        $("#"+id_part+"last_name").val(author.last_name);
        $("#"+id_part+"author_order_on_paper").val(author.order_on_paper);

    }
}


// add csrf-token to form
$(function() {

    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


});

function setOriginalFileName(){
    let file_input = document.getElementById("id_file-complete_file_path");
    let file = file_input.files[0];
    if (file !== undefined){
       $("#id_file-file_name").val(file.name);
    }
}

