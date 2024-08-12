function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function() {
	var csrftoken = getCookie('csrftoken');

	var	signupForm = document.getElementById("signup-form");
	var	signupUserName = document.getElementById("signup-username");
	var	signupPassword = document.getElementById("signup-password");
	var	signupConfirmPassword = document.getElementById("signup-confirm-password");
	var	closeButton = document.getElementById("signup-close-btn");

	// todo: print message on the
	// if (signupPassword != signupConfirmPassword)
	// 	return ;

	signupForm.addEventListener('submit', function(event) {
        event.preventDefault();

		//todo: compare signup confirm with password.
        const credentials = {
            'username': signupUserName.value,
            'password': signupPassword.value
        };
        fetch('/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
				'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(credentials)
        })
        .then(response => response.json())
		//todo: confirm signup.
        .then(data => {
			// todo if succeeded, close dialog box
			// else display error message
			console.log(data)
        });
    })
});
