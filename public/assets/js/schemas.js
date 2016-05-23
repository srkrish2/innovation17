$(init);
POST_URL = "/getschemas";
PROBLEM_ID = "3P6ENY9P79WU3BGAM63UL8VPD6QHIA";

function init() {
    var data = {
        "problem_id": PROBLEM_ID
    };
    $.ajax({
        type : "POST",
        url: POST_URL,
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        timeout : 100000,

        success : function(data) {
            var schemas = data["schemas"]
            for (i in schemas) {
                var schema = schemas[i]
                console.log("text: " + schema["text"])
                console.log("time: " + schema["time"])
                console.log("worker_id: " + schema["worker_id"])
                console.log("problem_id: " + schema["problem_id"])
            }
        },

        error : function(e) {
            console.log("ERROR: ", e);
        }
    });
}
