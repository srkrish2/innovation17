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
                if (language == "english") {
                    $('body').replaceWith("Thank you for participating. Your response has been submitted and we will get back to you shortly.")
                } else if (language == "chinese") {
                    $('body').replaceWith("非常感谢您的参与，你的答案已经提交。我们将很快联系您")
                } else if (language == "russian") {
                    $('body').replaceWith("Благодарим за участие. Ваши ответы приняты и мы скоро свяжемся с вами.")
                }
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