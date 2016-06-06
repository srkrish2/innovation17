(function(global){
    makePostRequest();
    var interval = setInterval(makePostRequest,30000);
    $(document).on('click', 'a.schemalist', function(e){
        clearInterval(interval);
    });
    $(document).on('click','div.button.publish',function(e){
        $.ajax({
            type: "post",
            url: "publish_problem",
            data: {
                problem_id: $e.val()
            },
            success: function(sdata){
                console.log("return back from sdata");
            }
        });
    });
    $(document).on('click','div.button.delete',function(e){
        $.ajax({
            type: "post",
            url: "publish_problem",
            data: {
                problem_id: $e.val()
            },
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
            console.log('data = '+sdata);
            for (var i= 0;i<sdata.length; i++){
                $('tr.'+sdata[i]['problem_id']+' .schema-list')[0].innerHTML=sdata[i]['count'];
            }
        }
    })
}