$(".submit").click(function() {
    var summary = $(".summary").val()
    var similar = $(".similar").val()
    var schema = $(".schema").val()
    var worker_id = $(".worker_id").val()
    var problem_id = $(".problem_id").val()
    var language = $(".language").val()
    var data = {
        "type": "schema1",
        "summary": summary,
        "similar": similar,
        "schema": schema,
        "worker_id": worker_id,
        "problem_id": problem_id,
        "language": language
    }
    if (summary && similar && schema) {
        $.ajax({
            type : "POST",
            url: "/submit_task",
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function(data) {
                window.location.replace(data["url"])
            }
        })
    } else {
        if (language == "english") {
            window.alert("Please fill out all fields")
        } else if (language == "chinese") {
            window.alert("请回答所有问题")
        } else if (language == "russian") {
            window.alert("Пожалуйста, заполните все поля")
        }
    }
});