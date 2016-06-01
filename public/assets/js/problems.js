(function(global){
    // $(document).on('click','.schema-list',function(e){
    //     e.preventDefault();
    //     console.log('we enter schemalist-'+e);
    //     $.ajax({
    //         type: 'GET',
    //         URL:'/getschema',
    //         data: $(this).url,
    //         success: function(sdata){
    //             console.log('get schema!');
    //         },
    //         error: function(e){
    //             console.log(e);
    //         }
    //     });
    // });
    // for (pid in {'sdata':"hello",'spanish':'halo'}){
    //                 console.log(pid);
    //                 //$('tr.'+pid).innerHTML=0;
    //             }
    setInterval(function(){
        // var project_num = $('tr').length-2, project_ids = [];
        // for (var i=0; i<project_num; i+=1) {
        //     project_ids.push($('tr')[i+1]);
        // }
        console.log('setInterval');
        $.ajax({
            type: "GET",
            url: '/get_schema_count_updates',
            success:function(sdata){
                console.log('suc');
                for (var i= 0;i<sdata.length; i++){
                    $('tr.'+sdata[i]['problem_id']+' > .schema-list').innerHTML=10;
                }            
            }
        })
    },3000);
}(window))