(function(global){
    var interval = setInterval(function(){
        // var project_num = $('tr').length-2, project_ids = [];
        // for (var i=0; i<project_num; i+=1) {
        //     project_ids.push($('tr')[i+1]);
        // }
        console.log('setInterval');
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
    },30000);
    $(document).on('click', 'a.schemalist', function(e){
        clearInterval(interval);
    });
    

}(window));