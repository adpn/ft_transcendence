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

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", async (event) => {
        if (event.target.matches("#remove-friend")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleRemoveFriend(relationId);
        }

        if (event.target.matches("#add-friend")) {
            event.preventDefault();
            const userId = event.target.getAttribute('data-user-id');
            await handleAddFriend(userId);
        }

        if (event.target.matches("#cancel-request")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleCancelRequest(relationId);
        }

        if (event.target.matches("#accept-request")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleAcceptRequest(relationId);
        }

        if (event.target.matches("#decline-request")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleDeclineRequest(relationId);
        }

    });
});

async function handleRemoveFriend(relationId) {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`/friend/remove_friend/${relationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    data = await response.json();
    user_id = data['user_id'];

    if (response.ok) {
        friendship = document.getElementById('friendship');
        friendship.innerHTML = `
            <button class="btn btn-primary" id="add-friend" data-user-id=${user_id}>Add Friend</button>
        `;
    } else {
        alert('Failed to remove friend.');
    }
}

async function handleAddFriend(userId) {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`/friend/add_friend/${userId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    data = await response.json();
    friendship_id = data['friendship_id'];

    if (response.ok) {
        friendship = document.getElementById('friendship');
        friendship.innerHTML = `
        <p>Pending Request</p>
        <button class="btn btn-danger" id="cancel-request" data-relation-id=${friendship_id}>Cancel Request</button>
    `;

    } else {
        alert('Failed to add friend.');
    }
}

async function handleCancelRequest(relationId) {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`/friend/cancel_friend_request/${relationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    data = await response.json();
    user_id = data['user_id'];

    if (response.ok) {
        friendship = document.getElementById('friendship');
        friendship.innerHTML = `
            <button class="btn btn-primary" id="add-friend" data-user-id=${user_id}>Add Friend</button>
        `;
    } else {
        alert('Failed to cancel the request.');
    }
}

async function handleAcceptRequest(relationId) {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`/friend/accept_friend/${relationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    data = await response.json();
    friendship_id = data['friendship_id'];
    if (response.ok) {
        friendship = document.getElementById('friendship');
        friendship.innerHTML = `
            <p>Friend</p>
            <button class="btn btn-danger" id="remove-friend" data-relation-id=${friendship_id}>Remove Friend</button>
        `;
    } else {
        alert('Failed to accept the request.');
    }
}

async function handleDeclineRequest(relationId) {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`/friend/decline_friend/${relationId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });

    data = await response.json();
    user_id = data['user_id'];

    if (response.ok) {
        friendship = document.getElementById('friendship');
        friendship.innerHTML = `
            <button class="btn btn-primary" id="add-friend" data-user-id=${user_id}>Add Friend</button>
        `;
    } else {
        alert('Failed to decline the request.');
    }
}

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