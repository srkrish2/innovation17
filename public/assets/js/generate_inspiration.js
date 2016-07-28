$(".submit").click(function() {
    var summary = $(".summary").val()
    var reason = $(".reason").val()
    var source_link = $(".source_link").val()
    var image_link = $(".image_link").val()
    var worker_id = $(".worker_id").val()
    var problem_id = $(".problem_id").val()
    var data = {
        "type": "inspiration",
        "summary": summary,
        "reason": reason,
        "source_link": source_link,
        "image_link": image_link,
        "worker_id": worker_id,
        "problem_id": problem_id
    }
    if (summary && reason && source_link && image_link && worker_id && problem_id) {
        $.ajax({
            type : "POST",
            url: "/submit_task",
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function() {
                window.location.replace("/idea");
//                $('body').replaceWith("Your input has been recorded, thank you.")
            }
        })
    } else {
        window.alert("Please fill out all fields")
    }
});