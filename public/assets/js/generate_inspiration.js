var TIMER_MIN = 20 //for testing, original 20
var language = $(".language").val()

$(document).ready(function(){
//    var countDownDate = new Date();
//    countDownDate.setMinutes(start.getMinutes() + 20);
//
//    // Update the count down every 1 second
//    var x = setInterval(function() {
//
//      // Get todays date and time
//      var now = new Date().getTime();
//
//      // Find the distance between now an the count down date
//      var distance = countDownDate - now;
//
//      // Time calculations for days, hours, minutes and seconds
//      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
//      var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
//      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
//      var seconds = Math.floor((distance % (1000 * 60)) / 1000);
//
//      // Display the result in the element with id="demo"
//      document.getElementById("demo").innerHTML = minutes + "m " + seconds + "s ";
//
//      // If the count down is finished, write some text
//      if (distance < 0) {
//        clearInterval(x);
//        document.getElementById("demo2").innerHTML = "EXPIRED";
//      }
//    }, 1000);

    $(".submit").click(function() {
            var now = new Date().getTime()
            var delta = now - start
            var delta_min = Math.floor( delta / (60 * 1000) )

            var timer = ''

            if (delta_min < TIMER_MIN) {
                if (language == "english") {
//                    timer = "Please spend at least " + TIMER_MIN + " min on this task. It's been "+delta_min+ " min"
                    window.alert("Please spend at least " + TIMER_MIN + " min on this task. It's been "+delta_min+ " min")
                } else if (language == "chinese") {
                    timer = '<font color="red" size="2">' +"请用至少 " + TIMER_MIN + " 分钟来完成这个任务。你已经工作了 "+delta_min+" 分钟。" + '</font>'
                    $("#demo").html(timer);
//                    window.alert("请用至少 " + TIMER_MIN + " 分钟来完成这个任务。你已经工作了 "+delta_min+" 分钟。")
                } else if (language == "russian") {
//                    timer = "Пожалуйста, проведите над заданием как минимум " + TIMER_MIN + " мин. Прошло "+delta_min + " мин."
                    window.alert("Пожалуйста, проведите над заданием как минимум " + TIMER_MIN + " мин. Прошло "+delta_min + " мин.")
                }

//                $("#dialogtext").html(timer);
//                $("#dialog1").dialog('open');
                return
            }


        var problem_id = $(".problem_id").val()
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
            var s = ''
            if (language == "english") {
                s = "Please fill out all fields"
//                window.alert("Please fill out all fields")
            } else if (language == "chinese") {
                s = "请回答所有问题"
//                window.alert("请回答所有问题")
            } else if (language == "russian") {
                s = "Пожалуйста, заполните все поля"
//                window.alert("Пожалуйста, заполните все поля")
            }
            $("#fill").html(s);
        }
    });
})

var start = new Date().getTime()
function tenMinAlert(){
    var timer = ''
    if (language == "english") {
//        timer = "It has been "+TIMER_MIN+" min since you've started. " +
//                 "Please finish the task in the next 10 min to not go overtime."
        window.alert("It has been "+TIMER_MIN+" min since you've started. " +
                 "Please finish the task in the next 10 min to not go overtime.")
    } else if (language == "chinese") {
        timer = '<font color="red" size="2">' + "你已经工作了 "+TIMER_MIN+" 分钟。还有十分钟剩余，请在十分钟之内完成这个任务。" + '</font>'
        document.getElementById("demo").innerHTML = timer
//        window.alert("你已经工作了 "+TIMER_MIN+" 分钟。还有十分钟剩余，请在十分钟之内完成这个任务。")
    } else if (language == "russian") {
//        timer = "Прошло "+TIMER_MIN+" мин с начала задания. Постарайтесь в течении следующих 10 мин."
        window.alert("Прошло "+TIMER_MIN+" мин с начала задания. Постарайтесь в течении следующих 10 мин.")
    }

}
setTimeout(tenMinAlert,TIMER_MIN*1000*60);
