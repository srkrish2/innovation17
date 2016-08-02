
var POST_URL = "/post_sign_in";
var LOGIN_SELECTOR = ".login.ui.form";


var VALIDATION_RULES = {
    fields: {
        Loginusername: {
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter your email or username'
            }
            ]
        },
        Loginpassword: {
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter your password'
            }
            ]
        }
    }
};

$(document).on('click','.ui.button.submit.login',function(e){
    $(e.currentTarget).prop('disabled',true);
    $(LOGIN_SELECTOR).form(VALIDATION_RULES);
    if($(LOGIN_SELECTOR).form('is valid')){
        var name = $(LOGIN_SELECTOR).form("get value", "Loginusername");
        var password = $(LOGIN_SELECTOR).form("get value", "Loginpassword");
        var data = {
            "name": name,
            "password": password
        };
        console.log("data is"+data)
        $.ajax({
            type : "POST",
            url: POST_URL,
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            timeout : 100000,

            success : function(data) {
                $(e.currentTarget).prop('disabled',false);
                if (data["success"]) {
                    window.location.replace("/"+data["url"]);
                } else {
                    $(LOGIN_SELECTOR).form("add errors", ["Your email or password was incorrect. Please try again."]);
                }
            },

            error : function(e) {
                console.log("ERROR: ", e);
            }
        });
        e.preventDefault();
    }
})



var REG_SELECTOR = '.register.ui.form';
var REG_RULES = {
    fields: {
        username: {
            rules: [
            {
                type   : 'empty',
                prompt : 'Please enter your username'
            },
            {
                type: 'regExp[/^[a-z0-9_-]{6,16}$/]',
                prompt: "Please enter a 6-16 letter username"
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
        password2: {
            identifier  : 'password2',
            rules: [
            {
                type   : 'match[password]',
                prompt : 'Please enter the same password as above'
            }
            ]
        }
    }
};

$(document).on('click', '.profileregister', function(e){
    $(REG_SELECTOR).form(REG_RULES);
    $(REG_SELECTOR).form('validate form');
    if($(REG_SELECTOR).form('is valid')){
        $(e.currentTarget).prop('disabled',true);
        e.preventDefault();
        console.log("i am in");
        var username = $(REG_SELECTOR).form('get value','username'),
        password = $(REG_SELECTOR).form('get value', 'password'),
        email = $(REG_SELECTOR).form('get value','email');
        $.ajax({
            type: 'POST',
            url: '/post_new_account',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                'username': username,
                'password': password,
                'email': email
            }),

            success: function(sdata){
                $(e.currentTarget).prop('disabled',false);
                if (sdata["success"]) {
                    window.location.replace("/"+sdata["url"]);
                } else {
                    console.log("success=false");
                }
            },
            error: function(e){
                console.log('error in register: '+e);
            }
        });
    }
});