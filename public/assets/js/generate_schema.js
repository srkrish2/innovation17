$(".submit").click(function() {
    var summary = $(".summary").val()
    var similar = $(".similar").val()
    var schema = $(".schema").val()
    var worker_id = $(".worker_id").val()
    var problem_id = $(".problem_id").val()
    var data = {
        "type": "schema",
        "summary": summary,
        "similar": similar,
        "schema": schema,
        "worker_id": worker_id,
        "problem_id": problem_id
    }
    console.log(data)
    if (summary && similar && schema && worker_id && problem_id) {
        $.ajax({
            type : "POST",
            url: "/submit_task",
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function(data) {
                window.location.replace("/schema2");
//                $('body').replaceWith("Your input has been recorded, thank you.");
            }
        })
    } else {
        window.alert("Please fill out all fields")
    }
});