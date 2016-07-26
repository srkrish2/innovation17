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
    // checkNewReaction();
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
            "schema_assignments_num": schemagoal
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

function checkNewReaction(){
    var temp = new Date().getTime();
    console.log("it has been " + (temp-begin)/1000);
        // begin = new Date().getTime();
        $.ajax({
            type: "GET",
            url: '/get_count_updates',
            success:function(sdata){

                for (var i= 0;i<sdata.length; i++){
                    $('<tr class="reaction-id item "'+sdata[i]['id']+'>'
                        + '<td class="reaction text">'+sdata[i]['text'] + '"</td>'
                        + '<td class="rating novelty"><div class="ui star rating" data-rating="'+sdata[i]['novelty']+'"</div></td>'
                        + '<td class="rating applicability"><div class="ui star rating" data-rating="'+sdata[i]['applicability']+'"</div></td>'+
                        + '<td class="rating affecting_problem"><div class="ui star rating" data-rating="'+sdata[i]['affecting_problem']+'"</div></td>'+
                        + '<td class="rating affecting_solution"><div class="ui star rating" data-rating="'+sdata[i]['affecting_solution']+'"</div></td>'+
                        +'</div>');
                    if($('tr.'+sdata[i]['problem_id']+' .inspiration-list').length)$('tr.'+sdata[i]['problem_id']+' .inspiration-list')[0].innerHTML="<i class='write icon'></i> "+sdata[i]['inspiration_count'];
                    if($('tr.'+sdata[i]['problem_id']+' .idea-list').length)$('tr.'+sdata[i]['problem_id']+' .idea-list')[0].innerHTML="<i class='idea icon'></i> "+sdata[i]['idea_count'];
                    if($('tr.'+sdata[i]['problem_id']+' .suggestion-list').length)$('tr.'+sdata[i]['problem_id']+' .suggestion-list')[0].innerHTML="<i class='doctor icon'></i> "+sdata[i]['suggestion_count'];
                }
                console.log('within makerequest, after success return');
                timeoutID = setTimeout(makePostRequest,10000);
            }
        })
    }
