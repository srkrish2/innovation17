$(init);

var POST_URL = "/submit_newproject";
var SELECTOR = ".ui.form";

var VALIDATION_RULES = {
    fields: {
        title: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please enter your email or username'
                }
            ]
        },
        description: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please enter your password'
                }
            ]
        },
        category: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please choose a category'
                }
            ]
        }
    },
    onSuccess: submitForm
};


function init() {
    $(SELECTOR).form(VALIDATION_RULES);
    $('.ui.fluid.search.selection.dropdown').dropdown();
    $('#addtags').keyup(function(e){
        if (e.which == 13) {
            $("<div class = 'ui olive new-tag label'>"+this.value+" <i class='delete icon'></i></div>").insertAfter(".icon.tags");
            console.log("this is");
            console.log(this);
            $(this).val('');
        }
    });
    $(document).on('click', 'i.delete', function(e){
        console.log(e);
        $(this).parent().remove();
    });
}

function submitForm(e) {
    var title = $(SELECTOR).form("get value", "title");
    var description = $(SELECTOR).form("get value", "description");
    var category = $(SELECTOR).form("get value", "category");

    var data = {
            "title": title,
            "description": description,
            "category": category
        }
    $.ajax({
        type : "POST",
        url: POST_URL,
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        timeout : 100000,

        success : function(data) {
            window.location.replace("/"+data["url"]);
        },

        error : function(e) {
            console.log("ERROR: ", e);
        }
    });
    e.preventDefault();
}