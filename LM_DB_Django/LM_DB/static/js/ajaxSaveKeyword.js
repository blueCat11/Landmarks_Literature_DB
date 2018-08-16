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

        if(json.hasOwnProperty('keyword_pk')) {
            $('#id_new_keyword-keyword').val(''); // remove the value from the input
            let keyword_pk = json.keyword_id;
            let new_keyword_element = '<li><label for="id_paper_keywords-paperKeywords_' +
                keyword_pk + '"><input name="paper_keywords-paperKeywords" value="' +
                keyword_pk + '" id="id_paper_keywords-paperKeywords_' +
                keyword_pk + '" type="checkbox"> ' +
                String(keyword) + '</label> </li>';

            $("#id_paper_keywords-paperKeywords").append(new_keyword_element);
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

