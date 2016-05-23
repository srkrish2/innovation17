$(init);

var POST_URL = "/authorize";
var SELECTOR = ".ui.form";

function init() {
    $(SELECTOR).form(VALIDATION_RULES);
}

var VALIDATION_RULES = {
    fields: {
        name: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please enter your email or username'
                }
            ]
        },
        password: {
            rules: [
                {
                    type   : 'empty',
                    prompt : 'Please enter your password'
                }
            ]
        }
    },
    onSuccess: submitForm
};

function submitForm(e) {
    var name = $(SELECTOR).form("get value", "name");
    var password = $(SELECTOR).form("get value", "password");
    var data = {
            "name": name,
            "password": password
        };
    $.ajax({
        type : "POST",
        url: POST_URL,
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        timeout : 100000,

        success : function(data) {
            if (data["success"]) {
                window.location.replace("/"+data["url"]);
            } else {
                $(SELECTOR).form("add errors", ["Your email or password was incorrect. Please try again."]);
            }
        },

        error : function(e) {
            console.log("ERROR: ", e);
        }
    });
    e.preventDefault();
}