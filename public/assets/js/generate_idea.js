var TIMER_MIN = 20 //for testing, original 20
var language = $(".language").val()
var start = new Date().getTime()
setTimeout(tenMinAlert,TIMER_MIN*1000*60);

$(document).ready(function(){
    $(".submit").click(function() {
        var now = new Date().getTime()
        var delta = now - start
        var delta_min = Math.floor( delta / (60 * 1000) )
        if (delta_min < TIMER_MIN) {
            if (language == "english") {
                window.alert("Please spend at least " + TIMER_MIN + " min on this task. It's been "+delta_min+ " min")
            } else if (language == "chinese") {
                window.alert("请用至少 " + TIMER_MIN + " 分钟来完成这个任务。你已经工作了 "+delta_min+" 分钟。")
            } else if (language == "russian") {
                window.alert("Пожалуйста, проведите над заданием как минимум " + TIMER_MIN + " мин. Прошло "+delta_min + " мин.")
            }
            return
        }

        var explanation = $(".explanation").val()
        var idea = $(".idea").val()
        var worker_id = $(".worker_id").val()
        var problem_id = $(".problem_id").val()
        var data = {
            "type": "idea",
            "explanation": explanation,
            "idea": idea,
            "worker_id": worker_id,
            "problem_id": problem_id,
            "language": language
        }
        if (explanation && idea) {
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
})

function tenMinAlert(){
    if (language == "english") {
        window.alert("It has been "+TIMER_MIN+" min since you've started. " +
                 "Please finish the task in the next 10 min to not go overtime.")
    } else if (language == "chinese") {
        window.alert("你已经工作了 "+TIMER_MIN+" 分钟。还有十分钟剩余，请在十分钟之内完成这个任务。")
    } else if (language == "russian") {
        window.alert("Прошло "+TIMER_MIN+" мин с начала задания. Постарайтесь в течении следующих 10 мин.")
    }
}
