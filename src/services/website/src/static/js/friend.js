import { navigateTo } from './router.js';
import { getCookie } from './auth.js';

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

	const form = document.getElementById('userSearchForm');
	const input = document.getElementById('userSearchInput');

	form.addEventListener('submit', (event) => {
		event.preventDefault();
		if (input.value) {
			navigateTo(`/user/${input.value}`);
		}
		input.value = '';
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
	const data = await response.json();
	const user_id = data['user_id'];

	if (response.ok) {
		const friendship = document.getElementById('friendship');
		friendship.innerHTML = `
			<p>You are not friend !</p>
			<button class="btn btn-outline-success" id="add-friend" data-user-id=${user_id}>Add Friend</button>
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
	const data = await response.json();
	const friendship_id = data['friendship_id'];

	if (response.ok) {
		const friendship = document.getElementById('friendship');
		friendship.innerHTML = `
		<p>You sent them a friend request !</p>
		<button class="btn btn-outline-danger" id="cancel-request" data-relation-id=${friendship_id}>Cancel Request</button>
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
	const data = await response.json();
	const user_id = data['user_id'];

	if (response.ok) {
		const friendship = document.getElementById('friendship');
		friendship.innerHTML = `
			<p>You are not friend !</p>
			<button class="btn btn-outline-success" id="add-friend" data-user-id=${user_id}>Add Friend</button>
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
	const data = await response.json();
	const friendship_id = data['friendship_id'];
	if (response.ok) {
		const friendship = document.getElementById('friendship');
		friendship.innerHTML = `
			<p>You are friend already !</p>
			<button class="btn btn-outline-danger" id="remove-friend" data-relation-id=${friendship_id}>Remove Friend</button>
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

	const data = await response.json();
	const user_id = data['user_id'];

	if (response.ok) {
		const friendship = document.getElementById('friendship');
		friendship.innerHTML = `
			<p>You are not friend !</p>
			<button class="btn btn-outline-success" id="add-friend" data-user-id=${user_id}>Add Friend</button>
		`;
	} else {
		alert('Failed to decline the request.');
	}
}
