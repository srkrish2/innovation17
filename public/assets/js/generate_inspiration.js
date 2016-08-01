$(".submit").click(function() {
    var problem_id = $(".problem_id").val()
    var language = $(".language").val()
    var worker_id = $(".worker_id").val()
    var source_link = $(".source_link").val()
    var image_link = $(".image_link").val()
    var summary = $(".summary").val()
    var reason = $(".reason").val()
    var data = {
        "type": "inspiration",
        "problem_id": problem_id,
        "language": language,
        "worker_id": worker_id,
        "source_link": source_link,
        "image_link": image_link,
        "summary": summary,
        "reason": reason
    }
    if (source_link && image_link && summary && reason) {
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