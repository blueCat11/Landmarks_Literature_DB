
function saveNewConceptName(){
    let conceptName = $('#id_concept_name-concept_name').val();

$.ajax({
    url : "/LM_DB/enterData/", // the endpoint
    type : "POST", // http method
    data : {
        isNewConceptName: true,
        concept_name: conceptName,
    }, // data sent with the post request

    // handle a successful response
    success : function(json) {
        if(json.hasOwnProperty('concept_name_id')) {
            $('#id_concept_name-concept_name').val(''); // remove the value from the input
            let concept_name_pk = json.concept_name_id;
            let new_concept_name_element = '<li><label for="id_concept_name-paper_concept_name_' +
                concept_name_pk + '"><input name="concept-name-paper_concept_name" value="' +
                concept_name_pk + '" id="id_concept_name-paper_concept_name_' +
                concept_name_pk + '" type="checkbox"> ' +
                String(conceptName) + '</label> </li>';

            $("#id_concept_name-paper_concept_name").append(new_concept_name_element);
        }else if (json.hasOwnProperty('error')){
            $('#add_concept_name').after('<div class="error">'+json.error+'</div>')
        }
        console.log("success"); // another sanity check
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    });
}


function saveNewCategory(){
    let category_name = $('#id_new_category-category_name').val();
    let shortcut = $('#id_new_category-shortcut').val();
    let description = $('#id_new_category-description').val();
    let super_category = $('input[name=new_category-super_category]:checked', '#id_new_category-super_category').val();


$.ajax({
    url : "/LM_DB/enterData/", // the endpoint
    type : "POST", // http method
    data : {
        isNewCategory: true,
        category_name: category_name,
        shortcut: shortcut,
        description: description,
        super_category: super_category
    }, // data sent with the post request

    // handle a successful response
    success : function(json) {
        if(json.hasOwnProperty('category_id')) {
            // remove the value from the input
            $('#id_new_category-category_name').val('');
            $('#id_new_category-shortcut').val('');
            $('#id_new_category-description').val('');
            $('input[name=new_category-super_category]:checked', '#id_new_category-super_category').prop('checked', false); //TODO this might be cause for trouble... not tested yet

            //add the new category to the list
            let category_pk = json.category_id;
            let new_category_element = '<li><label for="id_paper_categories-paper_categories_' +
                category_pk + '"><input name="paper_categories-paper_categories" value="' +
                category_pk + '" id="id_paper_categories-paper_categories_' +
                category_pk + '" type="checkbox"> ' +
                String(category_name) + '</label> </li>';

            $("#id_paper_categories-paper_categories").append(new_category_element);
        }else if (json.hasOwnProperty('error')){
            $('#add_categories').after('<div class="error">'+json.error+'</div>')
        }
        console.log("success"); // another sanity check
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    });

}


function saveNewKeyword(){
let keyword = $('#id_new_keyword-keyword').val();

$.ajax({
    url : "/LM_DB/enterData/", // the endpoint
    type : "POST", // http method
    data : {
        isNewKeyword: true,
        keyword: keyword,
    }, // data sent with the post request

    // handle a successful response
    success : function(json) {
        if(json.hasOwnProperty('keyword_id')) {
            $('#id_new_keyword-keyword').val(''); // remove the value from the input
            let keyword_pk = json.keyword_id;
            let new_keyword_element = '<li><label for="id_paper_keywords-paper_keywords_' +
                keyword_pk + '"><input name="paper_keywords-paper_keywords" value="' +
                keyword_pk + '" id="id_paper_keywords-paper_keywords_' +
                keyword_pk + '" type="checkbox"> ' +
                String(keyword) + '</label> </li>';

            $("#id_paper_keywords-paper_keywords").append(new_keyword_element);
            console.log(new_keyword_element)
            console.log("new keyword element")
        }else if (json.hasOwnProperty('error')){
            $('#add_keywords').after('<div class="error">'+json.error+'</div>')
        }
        console.log("success"); // another sanity check
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    });

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

