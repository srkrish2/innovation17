(function(global){
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
        },
        onSuccess: submitregister
    };

    function submitregister(e){
        e.preventDefault();
        console.log("i am in");
        var username = $('.ui.form').form('get value','username'),
        password = $('.ui.form').form('get value', 'password'),
        email = $('.ui.form').form('get value','email');
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

    $('.ui.form').form(REG_RULES);
}(window));