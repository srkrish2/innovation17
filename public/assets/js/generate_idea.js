$(".submit").click(function() {
    var explanation = $(".explanation").val()
    var idea = $(".idea").val()
//    var worker_id = $(".worker_id").val()
    var problem_id = $(".problem_id").val()
    var data = {
        "type": "idea",
        "explanation": explanation,
        "idea": idea,
//        "worker_id": worker_id,
        "problem_id": problem_id
    }
    if (explanation && idea && problem_id) {
        $.ajax({
            type : "POST",
            url: "/submit_task",
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function() {
                $('body').replaceWith("bye.")
//                $('body').replaceWith("Your input has been recorded, thank you.");
            }
        })
    } else {
        window.alert("Please fill out all fields")
    }
});