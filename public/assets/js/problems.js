(function(global){
    makePostRequest();
    var interval = setInterval(makePostRequest,10000);
    $(document).on('click', 'a.schemalist, div.button', function(e){
        clearInterval(interval);
    });
    $(document).on('click','div.button.publish',function(e){
        e.preventDefault();
        $(e.currentTarget).innerHTML="<i class='paw icon'></i>0";
        var rowclass = $(e.currentTarget.parentElement.parentElement).attr('class');
        $.ajax({
            type: "POST",
            url: "/publish_problem",
            contentType: "application/json",
            data: JSON.stringify({
                "problem_id": rowclass
            }),
            success: function(sdata){
                console.log("return back from sdata");
                // if(sdata['success'])$(e.currentTarget.parentElement.parentElement).attr('class',sdata['new_id']);
                $('tr.'+rowclass+' .ui.button.edit').addClass('hidden');
                $('tr.'+rowclass+' .ui.button.delete').addClass('hidden');
                $('tr.'+rowclass+' .ui.button.publish').addClass('hidden');
                $('tr.'+rowclass+' .ui.button.view').removeClass('hidden');
                makePostRequest();
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
    // get total seconds between the times
    // var delta = Math.abs(date_future - date_now) / 1000;

    // // calculate (and subtract) whole days
    // var days = Math.floor(delta / 86400);
    // if(days>3)return;

    $.ajax({
        type: "GET",
        url: '/get_count_updates',
        success:function(sdata){
            for (var i= 0;i<sdata.length; i++){
                $('tr.'+sdata[i]['problem_id']+' .schema-list')[0].innerHTML="<i class='sitemap icon'></i> "+sdata[i]['schema_count'];
                if($('tr.'+sdata[i]['problem_id']+' .inspiration-list').length)$('tr.'+sdata[i]['problem_id']+' .inspiration-list')[0].innerHTML="<i class='write icon'></i> "+sdata[i]['inspiration_count'];
                if($('tr.'+sdata[i]['problem_id']+' .idea-list').length)$('tr.'+sdata[i]['problem_id']+' .idea-list')[0].innerHTML="<i class='idea icon'></i> "+sdata[i]['idea_count'];
            }
        }
    })
}