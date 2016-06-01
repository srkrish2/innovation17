$(init);

var POST_URL = "/post_profile";
var SELECTOR = ".ui.form";

function init() {
    $(SELECTOR).form(VALIDATION_RULES);
    $('.ui.search.selection.dropdown').dropdown();
    $('#addtags').keyup(function(e){
        if (e.which == 188 || e.which == 13 || e.which == 186) { 
            var tag = "";
            if (e.which == 188 || e.which == 186) tag = this.value.trim().substring(0,this.value.length-1), REF = "";
            else tag = this.value.trim();
            if (tag.length == 0) return;
            if($('.new-tag.label').length === 0) {
                REF = ".icon.tags";
            }
            else {
                var InsIdx = $('.new-tag.label').length-1;
                REF = $('.new-tag.label')[InsIdx];
            }
            $("<div class = 'ui olive new-tag label'>" + tag
                                                       + " <i class='delete icon'></i></div>").insertAfter(REF);
            $(this).val('');
        }
    });
    $(document).on('click', 'i.delete', function(e){
        $(this).parent().remove();
    });
    $(document).on('click', 'div.button.profilesubmit', function(e){
        $.ajax({
            type: 'POST',
            data:{
                
            }
        })
    });
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
        },
        email: {
            identifier  : 'email',
            rules: [
            {
                type   : 'email',
                prompt : 'Please enter a valid e-mail'
            }
            ]
        },
        username: {
        identifier  : 'username',
        rules: [
          {
            type   : 'regExp[/^[a-z0-9_-]{4,16}$/]',
            prompt : 'Please enter a 4-16 letter username'
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