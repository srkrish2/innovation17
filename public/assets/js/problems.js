(function(global){
    makePostRequest();
    var interval = setInterval(makePostRequest,30000);
    $(document).on('click', 'a.schemalist, div.button', function(e){
        clearInterval(interval);
    });
    $(document).on('click','div.button.publish',function(e){
        e.preventDefault();
        $(e.currentTarget).innerHTML="<i class='paw icon'></i>0";
        $.ajax({
            type: "POST",
            url: "/publish_problem",
            contentType: "application/json",
            data: JSON.stringify({
                "problem_id": $(e.currentTarget.parentElement.parentElement).attr('class')
            }),
            success: function(sdata){
                console.log("return back from sdata");
                if(sdata['success'])$(e.currentTarget.parentElement.parentElement).attr('class',sdata['new_id']);
                $('tr.'+sdata['new_id']+' .ui.button.edit').addClass('hidden');
                $('tr.'+sdata['new_id']+' .ui.button.delete').addClass('hidden');
                $('tr.'+sdata['new_id']+' .ui.button.publish').addClass('hidden');
                $('tr.'+sdata['new_id']+' .ui.button.view').removeClass('hidden');
                makePostRequest();
                interval = setInterval(makePostRequest,30000);
                ///$('tr.'+sdata['new_id']+' .schema-list')[0].innerHTML="<i class='paw icon'></i>0";
            }
        });
    });
    $(document).on('click','div.button.delete',function(e){
        $(e.currentTarget.parentElement.parentElement).remove();
        $.ajax({
            type: "POST",
            url: "/delete_problem",
            contentType: 'application/json',
            data: JSON.stringify({
                "problem_id": $(e.currentTarget.parentElement.parentElement).attr('class')
            }),
            success: function(sdata){
                console.log("return back from sdata");
            }
        });
    });
}(window));

function makePostRequest(){
    $.ajax({
        type: "GET",
        url: '/get_count_updates',
        success:function(sdata){
            for (var i= 0;i<sdata.length; i++){
                $('tr.'+sdata[i]['problem_id']+' .schema-list')[0].innerHTML="<i class='paw icon'></i> "+sdata[i]['schema_count'];
                if($('tr.'+sdata[i]['problem_id']+' .inspiration-list').length)$('tr.'+sdata[i]['problem_id']+' .inspiration-list')[0].innerHTML="<i class='idea icon'></i> "+sdata[i]['inspiration_count'];
                if($('tr.'+sdata[i]['problem_id']+' .idea-list').length)$('tr.'+sdata[i]['problem_id']+' .idea-list')[0].innerHTML="<i class='gift icon'></i> "+sdata[i]['idea_count'];
            }
        }
    })
}