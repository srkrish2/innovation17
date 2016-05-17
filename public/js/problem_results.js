/*
 * problem_results.js
 * handles get results button
 */

$(init);

var GET_REQUEST_URL = "/getresults";
var BUTTON_ID = "#get-results";
var DIV_ID = "#results";

function init() {
    $(BUTTON_ID).click(function(e) {
        $(BUTTON_ID).prop("disabled",true);
        buttonClicked();
        e.preventDefault();
    });
}

function notify(serverResponse) {
    if (serverResponse == "FAIL") {
        $(DIV_ID).html("<p> Sorry, an error occurred. Please try again later. </p>");
    }
    else {
        $(DIV_ID).html(serverResponse);
    }
}

function buttonClicked() {
    console.log("get button pressed");
    $.ajax({
        type : "GET",
        url: GET_REQUEST_URL,
        // data: {"problem": problemText},
        timeout : 100000,

        success : function(string) {
            notify(string);
        },
        error : function(e) {
            console.log("ERROR: ", e);
        }
    });

}
