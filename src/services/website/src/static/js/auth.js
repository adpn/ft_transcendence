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

function successAlertPlaceholder(message) {
    var alertPlaceholder = document.getElementById('alert-placeholder');
    alertPlaceholder.innerHTML = `
        <div class="success-banner" id="success-alert" role="alert">
           ${message}
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

function updateAlertPlaceholderError(message) {
    var alertPlaceholder = document.getElementById('alert-placeholder');
    alertPlaceholder.innerHTML = `
        <div class="error-banner" role="alert">
            ${message}
        </div>
    `;
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

function handleLogout() {
    fetch('/auth/logout/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('auth_token')
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        successAlertPlaceholder('You have been logged out! Bye bye!');
        resetLoginButtons();
        navigateTo('/');
    });
}

// Function coming from signup.js, idk what it does
// async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
//     const token = localStorage.getItem('jwt'); // or sessionStorage.getItem('jwt')

//     const headers = {
//         'Authorization': `Bearer ${token}`, // Include token in the Authorization header
//         'Content-Type': 'application/json' // Optional, depending on the request type
//     };

//     return fetch(url, {
//         method: method,
//         headers: headers,
//         body: body ? JSON.stringify(body) : null
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Response Data:', data);
//         return data;
//     })
//     .catch(error => {
//         console.error('Request Error:', error);
//     });
// }

document.addEventListener("DOMContentLoaded", function() {

    fetch('/auth/is_authenticated/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('auth_token')
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 1) {
            localStorage.setItem('auth_token', data.token);
            replaceLoginButtons(data.user);
        }
    });

    var loginForm = document.getElementById("login-form");
    var loginUserName = document.getElementById("login-username");
    var loginPassword = document.getElementById("login-password");


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
                successAlertPlaceholder('Welcome!');
                replaceLoginButtons(data.user);
                localStorage.setItem('auth_token', data.token);
                navigateTo('/');
            }
            const loginModalElement = document.getElementById('loginModal');
            const loginModal = bootstrap.Modal.getInstance(loginModalElement);
            if (loginModal) {
                loginModal.hide();
            }
        });
    });

    // Signup form handling
    var signupForm = document.getElementById("signup-form");
    var signupUserName = document.getElementById("signup-username");
    var signupPassword = document.getElementById("signup-password");
    var signupConfirmPassword = document.getElementById("signup-confirm-password");

    signupForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const credentials = {
            'username': signupUserName.value,
            'password': signupPassword.value,
            'confirm_password': signupConfirmPassword.value
        };

        signupForm.reset();
        fetch('/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(credentials)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 0) {
                updateAlertPlaceholderError(data.message);
            } else {
                successAlertPlaceholder('Account successfully created! Welcome!');
                replaceLoginButtons(data.user);
                localStorage.setItem('auth_token', data.token);
                navigateTo('/');
            }
            const signUpModalElement = document.getElementById('signUpModal');
            const signUpModal = bootstrap.Modal.getInstance(signUpModalElement);
            if (signUpModal) {
                signUpModal.hide();
            }
        });
    });
});

window.handleLogout = handleLogout;
