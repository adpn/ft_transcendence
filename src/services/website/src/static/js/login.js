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

var token = null;

document.addEventListener("DOMContentLoaded", function() {
    var loginForm = document.getElementById("login-form");
    var loginUserName = document.getElementById("login-username");
    var loginPassword = document.getElementById("login-password");

    fetch('/auth/is_authenticated/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
			"Authorization": "Bearer " + localStorage.getItem("auth_token")
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 1) {
            localStorage.setItem('auth_token', data.token)
            replaceLoginButtons(data.user);
        }
    });

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const creds = {
            username: loginUserName.value,
            password: loginPassword.value
        };

        loginForm.reset();
        fetch('/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
				'Authorization': 'Bearer ' + localStorage.getItem('auth_token')
            },
            body: JSON.stringify(creds),
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 0) {
                updateAlertPlaceholderError(data.message);
            } else if (data.status === 1) {
                successAlertPlaceholder();
                replaceLoginButtons(data.user);
				localStorage.setItem('auth_token', data.token);
            }
            const loginModalElement = document.getElementById('loginModal');
            const loginModal = bootstrap.Modal.getInstance(loginModalElement);
            if (loginModal) {
                loginModal.hide();
            }
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
            <div class="success-banner" id="success-alert"  role="alert">
               Welcome !
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
                    <div class="profile-picture-container">
                        <img src="${user.profile_picture}" alt="${user.username}" class="profile-picture">
                    </div>
                </a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
                    <li><a href="/profile" class="dropdown-item" data-link>Profile</a></li>
                    <li><a href="/settings" class="dropdown-item" data-link>Settings</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" onclick="handleLogout()">Logout</a></li>
                </ul>
            </div>
        `;
    }

});
