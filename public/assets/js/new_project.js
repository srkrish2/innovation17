$(init);
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
        },
        schemagoal: {
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter the number of schemas that you want to gather for {name}'
            }
            ]
        }
    }
};


function init() {
    $(SELECTOR).form(VALIDATION_RULES);
    $('.ui.fluid.search.selection.dropdown').dropdown();
    $('#addtags').keyup(function(e){
        if (e.which == 188 || e.which == 13 || e.which == 186) { 
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

$(document).on('click','.ui.save, .ui.submit',function(e){
    // e.preventDefault();
    $(SELECTOR).form('validate form');
    if($(SELECTOR).form('is valid')){
        var id = $('.problem_id').innerHTML||null;
        var title = $(SELECTOR).form("get value", "title");
        var description = $(SELECTOR).form("get value", "description");
        var schemagoal = $(SELECTOR).form("get value", "schemagoal");

        var data = {
            "id": id,
            "title": title,
            "description": description,
            "schema_count_goal": schemagoal
        };
        var URL_link = "/post_new_problem";
        if($('.problem_id').innerHTML!=''){
            URL_link = "/post_problem_edit";
            $('.ui.loader.save-loader').addClass('active');
        }
        else if($(e.currentTarget).hasClass('save')){
            URL_link='/save_new_problem';
            $('.ui.loader.save-loader').addClass('active');
        }
        else $('.ui.loader.submit-loader').addClass('active');
        $.ajax({
            type : "POST",
            url: URL_link,
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function(data) {
                var success = data["success"]
                if (success) {
                    window.location.replace('/'+data['url']);
                } else {
                    console.log("UNEXPECTED ERROR")
                }
            },
            error : function(e) {
                console.log("ERROR: ", e);
            }
        });
    }
    
});
