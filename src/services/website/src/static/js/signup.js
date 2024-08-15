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

	signupForm.addEventListener('submit', function(event) {
        event.preventDefault();

		//todo: compare signup confirm with password.
        const credentials = {
            'username': signupUserName.value,
            'password': signupPassword.value,
            'confirm_password': signupConfirmPassword.value
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
        .then(data => {
			console.log(data)
            if (data.status === 0) {
                updateAlertPlaceholderError(data.message);
            } else {
                successAlertPlaceholder();
                replaceLoginButtons(data.user);
            }
            const signUpModalElement = document.getElementById('signUpModal');
            const signUpModal = bootstrap.Modal.getInstance(signUpModalElement);
            if (signUpModal) {
                signUpModal.hide();
            }
            signupForm.reset();
        });
    });

    function updateAlertPlaceholderError(message) {
        var alertPlaceholder = document.getElementById('alert-placeholder');
        alertPlaceholder.innerHTML = `
            <div class="error-banner" role="alert">
                ${message}
            </div>
        `;
    }

    function successAlertPlaceholder() {
        var alertPlaceholder = document.getElementById('alert-placeholder');
        alertPlaceholder.innerHTML = `
            <div class="success-banner" id="success-alert" role="alert">
               Account successfully created ! Welcome !
            </div>
    `;

    setTimeout(() => {
        var successAlert = document.getElementById('success-alert');
        successAlert.classList.add('fade-out');
        successAlert.addEventListener('transitionend', () => {
            successAlert.remove();
        });
    }, 3500);
    }

    function replaceLoginButtons(user) {
        var profileMenu = document.getElementById('profile-menu');
        profileMenu.innerHTML = `
            <div class="dropdown">
                <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" id="profileDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <span class="ms-2 me-2 text-white">${user.username}</span>
                    <img src="${user.profile_picture}" alt="${user.username}" class="rounded-circle" width="30" height="30">
                </a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
                <li><a href="/profile" class="dropdown-item" data-link>Profile</a></li>
                <li><a href="/settings" class="dropdown-item" data-link>Settings</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li class="dropdown-item" onclick="handleLogout()">Logout</li>
                </ul>
            </div>
        `;
    }
});
