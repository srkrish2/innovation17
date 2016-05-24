$(init);

var POST_URL = "/new_project";
var SELECTOR = ".ui.form";

var VALIDATION_RULES = {
    fields: {
        title: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please add a title'
                }
            ]
        },
        description: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please add description'
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
        if (e.which == 188 || e.which == 13 || e.which == 186) { // , enter ;
            var tag = "";
            if (e.which == 188 || e.which == 186) tag = this.value.trim().substring(0,this.value.length-1), REF = "";
            else tag = this.value.trim();
            if (tag.length == 0) return;
            if($('.new-tag.label').length === 0) {
                REF = ".icon.tags";
            }
            else {
                var InsIdx = $('.new-tag.label').length-1;
                REF = $('.new-tag.label')[InsIdx];
            }
            $("<div class = 'ui olive new-tag label'>" + tag
                                                       + " <i class='delete icon'></i></div>").insertAfter(REF);
            $(this).val('');
        }
    });
    $(document).on('click', 'i.delete', function(e){
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