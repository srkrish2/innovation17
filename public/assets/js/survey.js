$(".submit").click(function() {
    var worker_id = $(".worker_id").val()
    var language = $(".language").val()
    var age = $("input[name='age']").val()
    var gender = $("input[name='gender']:checked").val()
    var education = $("input[name='education']:checked").val()
    var expertise = $(".expertise").val()
    var foreign_lived = $("input[name='foreign_lived']:checked").val()
    var foreign_interact = $("input[name='foreign_interact']:checked").val()
    var data = {
        "type": "survey",
        "worker_id": worker_id,
        "language": language,
        "age": age,
        "gender": gender,
        "education": education,
        "expertise": expertise,
        "foreign_lived": foreign_lived,
        "foreign_interact": foreign_interact
    }
    if (age && gender && education && expertise && foreign_lived && foreign_interact) {
        $.ajax({
            type : "POST",
            url: "/submit_task",
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            success : function(data) {
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