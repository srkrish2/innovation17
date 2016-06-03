(function(global){
    makePostRequest()
    var interval = setInterval(makePostRequest,30000);
    $(document).on('click', 'a.schemalist', function(e){
        clearInterval(interval);
    });
}(window));

function makePostRequest(){
    $.ajax({
        type: "GET",
        url: '/get_count_updates',
        success:function(sdata){
            console.log('data = '+sdata);
            for (var i= 0;i<sdata.length; i++){
                $('tr.'+sdata[i]['problem_id']+' .schema-list')[0].innerHTML=sdata[i]['schema_count'];
            }
        }
    })
}