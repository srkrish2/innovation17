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
    $('.ui.fluid.search.selection.dropdown').dropdown('set selected','english');
    $('a[data-value="english"] > .delete').remove();
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
    $(document).ready(function(){
        $('.ui.rating')
        .rating({
            maxRating: 4,
            clearable: true
        });
    });

    //try out sample data
    var reaction = {
        'text':"How should we improve the wind noise control to filter out the wind while having necessary sirens within the realm of being heard?",
        'novelty':3,
        'applicability':2,
        'affecting_problem':1,
        'affecting_solution':3,
        'notes':['this is an interesting standpoint that is worth further investigation', 'good point'],
        'changed':false
    }
    //check to see if the new responses from Turkers coming in
}

$(document).on('click','.ui.save, .ui.submit',function(e){
    // e.preventDefault();
    $(SELECTOR).form('validate form');
    if($(SELECTOR).form('is valid')){
        var id = $('.problem_id').html()||null;
        var title = $(SELECTOR).form("get value", "title");
        var description = $(SELECTOR).form("get value", "description");
        var schemagoal = $(SELECTOR).form("get value", "schemagoal");
        var lazy = $('.ui.checkbox').checkbox('is checked')?true:false;
        var data = {
            "problem_id": id,
            "title": title,
            "lazy": lazy,
            "description": description,
            "schema_assignments_num": schemagoal,
            "languages":$('.ui.fluid.search.selection.dropdown').dropdown('get value').split(',')
        };
        var URL_link = null;
        $(e.currentTarget).prop('disabled',true);
        if($(e.currentTarget).hasClass('save')){
        URL_link = "/save_problem";//save a new_problem
    }
    else {
            URL_link = "/submit_problem";//post - make it public
            $('.ui.loader.submit-loader').addClass('active');
        }
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
                $(e.currentTarget).prop('disabled',false);
            },
            error : function(e) {
                console.log("ERROR: ", e);
            }
        });
    }
});