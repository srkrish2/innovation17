$(init);
URL = "/getproblems";

function init() {
    $.ajax({
        type : "GET",
        url: URL,
        timeout : 100000,

        success : function(data) {
            var problems = data["problems"]
            for (i in problems) {
                var problem = problems[i]
                console.log("problem_id: " + problem["problem_id"])
                console.log("schema_count: " + problem["schema_count"])
                console.log("description: " + problem["description"])
            }
        },

        error : function(e) {
            console.log("ERROR: ", e);
        }
    });
}
