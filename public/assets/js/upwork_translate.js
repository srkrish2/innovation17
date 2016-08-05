$(".submit").click(function() {
    var translation = $(".translation").val()
    var id = $(".id").val()
    var type = $(".type").val()
    var language = $(".language").val()
    var data = {
        "type": type,
        "id": id,
        "translation": translation,
        "language": language
    }
    $.ajax({
        type : "POST",
        url: "/submit_translation",
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        success : function(data) {
//            window.alert(JSON.stringify(data))
            if (!data["has_more"]) {
                $('body').replaceWith("You're done! We'll get back to you shortly.")
            } else {
                var id = data["id"]
                var original = data["original"]
                $("textarea#id").val(id)
                $("p#original").text(original)
                var count = $(".count").val()
                count -= 1
                $("h1").text(count+" left")
            }
        }
    })
})