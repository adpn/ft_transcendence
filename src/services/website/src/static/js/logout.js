import { navigateTo } from './router.js';

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

function handleLogout() {
	fetch('/auth/logout/', {
		method: 'GET',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
			"Authorization": "Bearer " + localStorage.getItem("auth_token")
		},
		credentials: 'include'
	})
	.then(response => response.json())
	.then(data => {
			successAlertPlaceholder();
			resetLoginButtons();
			navigateTo('/');
	});
}

window.handleLogout = handleLogout;

function resetLoginButtons() {
	var profileMenu = document.getElementById('profile-menu');
	profileMenu.innerHTML = `
		<ul class="navbar-nav ms-auto mb-2 mb-lg-0">
			<li class="nav-item">
				<button class="btn btn-primary me-2" data-bs-toggle="modal" data-bs-target="#loginModal">Log in</button>
			</li>
			<li class="nav-item">
				<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#signUpModal">Sign up</button>
			</li>
		</ul>
	`;
}

function successAlertPlaceholder() {
	var alertPlaceholder = document.getElementById('alert-placeholder');
	alertPlaceholder.innerHTML = `
		<div class="success-banner" id="success-alert"  role="alert">
		   You have been logged out ! Bye bye !
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

