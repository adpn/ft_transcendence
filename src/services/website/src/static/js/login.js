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

	loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

		//todo: compare login confirm with password.
        const credentials = {
            username: loginUserName.value,
            password: loginPassword.value
        };
        fetch('/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
				'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(credentials)
        })
        .then(response => response.json())
		//todo: confirm login.
        // .then(data => {
        //     fetchItems(); // Refresh the item list
        //     itemForm.reset(); // Clear the form
        // });
    })
});