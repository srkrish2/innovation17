/*
 * problem_entry.js
 * handles problem entry submission
 */

$(init);

var BUTTON_POST_URL = "/submit";
var BUTTON_ID = "#submit";
var DIV_ID = "#form-div";

function init() {
    $(BUTTON_ID).click(function(e) {
        $(BUTTON_ID).prop("disabled",true);
        buttonClicked();
        e.preventDefault();
    });
}

function notify(serverResponse) {
    if (serverResponse == "FAIL") {
        // TODO: don't replace everything in div, keep textarea
        $(DIV_ID).html("<p> Sorry, an error occurred. Please try again later. </p>");
    }
    else {
        // if not error, server returns the time
        var str1 = "<p> Problem received. Come back for the results after ";
        var str2 = str1.concat(serverResponse);
        var str3 = "</p>";
        var result = str2.concat(str3);
        $(DIV_ID).html(result);
    }
}

function buttonClicked() {
    // get the textarea input and send it over post request
    var problemText = $('textarea#problem').val();
    
    console.log("button pressed");
    $.ajax({
        type : "POST",
        url: BUTTON_POST_URL,
        data: {"problem": problemText},
        timeout : 100000,
         
        success : function(string) {
            notify(string);
        },
        error : function(e) {
            console.log("ERROR: ", e);
        }
    });

}
