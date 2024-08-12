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

	var	loginForm = document.getElementById("login-form");
	var	loginUserName = document.getElementById("login-username");
	var	loginPassword = document.getElementById("login-password");
	var	testButton = document.getElementById("test-button");

	loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

		//todo: compare login confirm with password.
        const creds = {
            username: loginUserName.value,
            password: loginPassword.value
        };

        fetch('/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(creds),
			credentials: 'include'
        })
        .then(response => response.json())
		//todo: confirm login.
        .then(data => {
			// todo if succeeded, close dialog box
			// else display error message
			console.log(data)
        });
    });

	testButton.addEventListener('click', function(event) { 
		event.preventDefault();

		fetch('/auth/protected/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken')
            },
			credentials: 'include'
        })
        .then(response => response.json())
		//todo: confirm login.
        .then(data => {
			// todo if succeeded, close dialog box
			// else display error message
			console.log(data)
        });

	});

});