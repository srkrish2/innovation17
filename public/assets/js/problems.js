(function(global){
    makePostRequest();
    var interval = setInterval(makePostRequest,30000);
    $(document).on('click', 'a.schemalist', function(e){
        clearInterval(interval);
    });
    $(document).on('click','div.button.publish',function(e){
        $.ajax({
            type: "POST",
            url: "/publish_problem",
            contentType: "application/json",
            data: JSON.stringify({
                "problem_id": $(e.currentTarget.parentElement.parentElement).attr('class')
            }),
            success: function(sdata){
                console.log("return back from sdata");
                if(sdata['success'])$(e.currentTarget.parentElement.parentElement).attr('class',sdata['new_id'])
            }
        });
    });
    $(document).on('click','div.button.delete',function(e){
        $.ajax({
            type: "POST",
            url: "/delete_problem",
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
            console.log('data = '+sdata[0]['count']);
            for (var i= 0;i<sdata.length; i++){
                $('tr.'+sdata[i]['problem_id']+' .schema-list')[0].innerHTML=sdata[i]['count'];
            }
        }
    })
}