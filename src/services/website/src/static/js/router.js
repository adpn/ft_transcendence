import { getCookie } from "./auth.js";

export const navigateTo = async url => {
    history.pushState(null, null, url);
    await router();
    // const matches = url.match('https://[^/]*/');
    // if (matches && matches.length) {
    //     window.dispatchEvent(new Event(url.substr(matches[0].length)));
    // }
};

// Router function to handle routes
const router = async () => {
    const routes = [
        { path: "/", view: Home },
        { path: "/game", view: Games },
        { path: "/settings", view: Settings },
        { path: "/friends", view: Friends },
        { path: "/stats", view: Stats },
        { path: "/user/:username", view: UserProfile }
    ];

    // Find a matching route or return 404
    const potentialMatches = routes.map(route => {
        const pathRegex = new RegExp("^" + route.path.replace(/:\w+/g, "(.+)") + "$");
        return {
            route: route,
            result: location.pathname.match(pathRegex)
        };
    });

    let match = potentialMatches.find(potentialMatch => potentialMatch.result);

    if (!match) {
        match = {
            route: { path: "/404", view: () => "<div class=\"text-center\"><h1>404 - Page Not Found</h1><p>Please go back to another page, using the buttons above.</p></div>" },
            result: [location.pathname]
        };
    }

    const params = match.result.slice(1);
    // Render the view
    document.getElementById('app').innerHTML = await match.route.view(...params);

	if (match.route.path == "/game")
		window.dispatchEvent(new Event("game"));
};

// View functions
const Home = () => `
    <div class="text-center">
        <h1>Home Page</h1>
        <p>Welcome to ft_transcendence!</p>
    </div>
`;

const Pong = () => `
<div class="row">
<div class="row text-center">
	<div class="canvas-container position-relative">
		<canvas id="gameCanvas" class="w-100 border"></canvas>
		<div id="game-menu" class="position-absolute top-50 start-50 translate-middle">
			<button class="btn btn-primary mb-2" id="quick-game-button" type="button">Quick Game</button>
		<br>
			<button class="btn btn-secondary" id="tournament-button" type="button">Tournament</button>
		</div>
	</div>
</div>
<div id="game-button-container" class="text-center mt-3">
	<button class="btn btn-success me-2" id="game-button" type="button">Find Game</button>
</div>
</div>
`;

const Games = async () => `
<div class="row">
<div class="row text-center">
	<div class="canvas-container position-relative" >
		<canvas id="gameCanvas" class="w-100 border"></canvas>
		<div id="game-ui" class="position-absolute top-0 start-0 w-100 h-100 flex-column align-items-center justify-content-center bg-dark">
		    <div id="loading-overlay" class="loading-overlay position-absolute top-0 start-0 w-100 h-100 flex-column align-items-center justify-content-center bg-dark" aria-hidden="true">
                <div class="spinner"></div>
		        <p class="text-light mt-3">Waiting for opponent...</p>
		        <div id="overlay-body" class=text-center></div>
    	    </div>
            <div id="game-menu" class="card position-absolute top-50 start-50 translate-middle bg-dark text-light" aria-hidden="true">
                <div id="game-menu-header" class="card-header d-flex flex-column justify-content-center align-items-center"></div>
                <div id="game-menu-body" class="card-body d-flex flex-column justify-content-center align-items-center"></div>
                <div id="game-menu-footer" class="card-footer d-flex flex-column justify-content-center align-items-center"></div>
            </div>
	    </div>
    </div>
</div>
<div id="game-button-container" class="text-center mt-3">
	<button class="btn btn-success me-2" id="game-button" type="button">Find Game</button>
</div>
</div>
`;

// todo: need a container that displays the participants. (a list ?)

const Settings = async () => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch('/auth/is_authenticated/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();

    if (data.status === 0) {
        return `
            <div class="text-center">
                <h1>Access Denied</h1>
                <p>You need to be logged in to view this page.</p>
            </div>
        `;
    }

    const { username, profile_picture } = data.user;

    return`
    <div class="text-center">
        <h1>Settings Page</h1>
        <p>Manage your profile settings here.</p>

        <!-- Change Profile Picture -->
        <div id="profile-picture-change" class="mb-3">
            <h4>Change Profile Picture</h4>
            <form id="profile-picture-form" enctype="multipart/form-data">
                <img src="${profile_picture}" alt="Profile Picture" class="profile-picture-preview">
                <br>
                <input type="file" id="profile-picture-input" name="profile_picture" accept="image/*" required>
                <br>
                <button type="submit" class="btn btn-primary mt-2">Upload</button>
            </form>
        </div>

        <!-- Change Username -->
        <div id="username-change" class="mb-3">
            <h4>Change Username</h4>
            <form id="username-change-form">
                <input type="text" id="new-username" name="username" value="${username}" placeholder="New Username" required>
                <br>
                <button type="submit" class="btn btn-primary mt-2">Change Username</button>
            </form>
        </div>

        <!-- Change Password -->
        <div id="password-change" class="mb-3">
            <h4>Change Password</h4>
            <form id="password-change-form">
                <input type="password" id="current-password" name="current_password" placeholder="Current Password" required>
                <br>
                <input type="password" id="new-password" name="new_password" placeholder="New Password" required>
                <br>
                <input type="password" id="confirm-new-password" name="confirm_new_password" placeholder="Confirm New Password" required>
                <br>
                <button type="submit" class="btn btn-primary mt-2">Change Password</button>
            </form>
        </div>
    </div>
    `;
};

const Friends = async () => {
    const app_content = 
    `
    <div class="text-center">
        <h1>Friends Page</h1>
        <div id="friend-requests">
            <h3>Friend Requests</h3>
            <ul id="friend-requests-list">
                <li>Loading friend requests list..</li>
            </ul>
        </div>
        <div id="friends">
            <h3>Friends List</h3>
            <ul id="friends-list">
                <li>Loading friends list..</li>
            </ul>
        </div>
    </div>
    `;

    document.getElementById('app').innerHTML = app_content;

    const token = localStorage.getItem('auth_token');
    const friendsList = await fetch('/friend/friend_list/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });

    const friendsData = await friendsList.json();

    if (friendsList.status === 401 || friendsData.status === 0) {
        document.getElementById('app').innerHTML =  `
            <div class="text-center">
                <h1>Access Denied</h1>
                <p>You need to be logged in to view this page.</p>
            </div>
        `;
        return document.getElementById('app').innerHTML;
    }

    if (friendsData.friends.length === 0) {
        document.getElementById('friends').innerHTML = `
            <h3>Friends List</h3>
            <p>You have no friend. How sad :-( </p>
        `;
    } else {
        const friendsList = document.getElementById("friends-list");
        friendsList.innerHTML = '';

        friendsData.friends.forEach(friend => {
            const listItem = document.createElement("div");

            listItem.innerHTML = `
                <div class="friend-item">
                    <div class="friend-info">
                        <div class="friend-picture-container">
                            <a href="/user/${friend.username}" data-link>
                                <img class="friend-picture" src="${friend.profile_picture}" alt="${friend.username}">
                            </a>
                    </div>
                    <span class="friend-name">${friend.username}</span>
                    <div class="online_status ${friend.is_online ? 'online' : 'offline'}"></div>
                </div>
            `;

        friendsList.appendChild(listItem);
        });
    }

    const friendRequests = await fetch('/friend/friend_requests_list/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });

    const friendsRequestsData = await friendRequests.json();
    if (friendsRequestsData.friend_requests.length === 0) {
        document.getElementById('friend-requests').innerHTML = `
            <h3>Friend Requests</h3>
            <p>Nobody wants to be your friend.</p>  
        `;
    } else {
        const friendRequestsList = document.getElementById("friend-requests-list");
        friendRequestsList.innerHTML = '';

        friendsRequestsData.friend_requests.forEach(friendRequest => {
            const listItem = document.createElement("div");
            listItem.innerHTML = `
                <div class="friend-request-item">
                    <div class="friend-info">
                        <div class="friend-picture-container">
                            <a href="/user/${friendRequest.username}" data-link>
                                <img class="friend-picture" src="${friendRequest.profile_picture}" alt="${friendRequest.username}">
                            </a>
                        </div>
                        <span class="friend-name">${friendRequest.username}</span>
                    </div>
                    <div class="friend-action-buttons">
                        <button class="btn btn-outline-success" id="accept-request-list" data-relation-id="${friendRequest.id}">Accept</button>
                        <button class="btn btn-outline-danger" id="decline-request-list" data-relation-id="${friendRequest.id}">Decline</button>
                    </div>
                </div>
            `;
        friendRequestsList.appendChild(listItem);
        });
    }
    return document.getElementById('app').innerHTML;
};

// change so that it manages two games, snake and pong
const Stats = async () => {
    const token = localStorage.getItem('auth_token');

    // Render the basic structure of the Stats page
    const app_content = `
    <div class="text-center">
        <h1>Stats Page</h1>
        <div id="total-stats">
            <span id="total-stats-content">Loading total stats...</span>
        </div>
        <div id="game-history">
            <h2>Game History</h2>
            <ul id="game-history-list">
                <li>Loading game history...</li>
            </ul>
        </div>
    </div>
    `;

    document.getElementById('app').innerHTML = app_content;

    const statsResponse = await fetch('/stat/personal_stats/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });

    const statsData = await statsResponse.json();

    if (statsResponse.status === 401) {
        document.getElementById('app').innerHTML = `
            <div class="text-center">
                <h1>Access Denied</h1>
                <p>You need to be logged in to view this page.</p>
            </div>
        `;
        return document.getElementById('app').innerHTML;
    }

    if (statsData.status === 0) {
        document.getElementById('app').innerHTML = `
            <div class="text-center">
                <h1>Stats Page</h1>
                <p>No games played yet.</p>
            </div>
        `;
        return document.getElementById('app').innerHTML;
    }

    document.getElementById("total-stats-content").textContent =
        `Total Games: ${statsData.pong.total_games} | Win percentage: ${statsData.pong.win_percentage}% | Average score: ${statsData.pong.average_score} | Precision: ${statsData.pong.precision}% | Total playtime: ${statsData.pong.playtime}`;

    const gameHistoryList = document.getElementById("game-history-list");
    gameHistoryList.innerHTML = '';

    statsData.pong.games.forEach(game => {
        const listItem = document.createElement("div");
        listItem.className = `game-stat ${game.is_winner ? 'victory' : 'defeat'}`;

        const resultText = game.is_winner ? 'Victory' : 'Defeat';
        listItem.innerHTML = `
            <strong>${resultText}</strong>&nbsp;| 
            Opponent:&nbsp;<a href="/user/${game.opponent}" class="text-white" data-link>${game.opponent}</a>&nbsp;|
            Score: ${game.personal_score} - ${game.opponent_score} |
            Duration: ${game.game_duration} |
            Date: ${new Date(game.game_date).toLocaleString()}
            `;

            gameHistoryList.appendChild(listItem);
        });

    return document.getElementById('app').innerHTML;
};

const UserProfile = async (username) => {
    const token = localStorage.getItem('auth_token');

    const response = await fetch(`/users/get_profile/${username}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${token}`
        }
    });
    const data = await response.json();

    if (response.status === 401) {
        return `
            <div class="text-center">
                <h2>Access Denied</h2>
                <p>You need to be logged in to view this page.</p>
            </div>
        `;
    }

    if (response.status === 404) {
        return `
            <div class="text-center">
                <h2>User Not Found</h2>
                <p>The user ${username} does not exist.</p>
            </div>
        `;
    }

    const app_content = `
    <div class="container text-center my-5">
        <img src="${data.profile_picture}" alt="${data.username}" class="rounded-circle mb-4 profile-picture-preview">
        <h1 class="fw-bold text-dark">${data.username}</h1>

        <div id="friendship" class="my-4"></div>
        
        <h3 class="mt-5 text-secondary">Stats</h3>
        <div id="user-stats" class="row justify-content-center mt-4"></div>
    </div>
    `;
    
    document.getElementById('app').innerHTML = app_content;

    const userStats = document.getElementById('user-stats');
    const friendship = document.getElementById('friendship');
    friendship.innerHTML = get_friendship_content(data.friendship, data.id);

    if (Object.keys(data.stats).length === 0) {
        userStats.innerHTML = `
        <div class="alert alert-info" role="alert">
            <p>No games played yet.</p>
        </div>
        `;
    }
    else {
        const pongStats = data.stats.pong;
        // need to add another check to differentiate between snake and pong
        userStats.innerHTML = `
        <div class="col-md-5 card p-4 mx-2 mb-4 shadow-sm">
            <p class="h5"><strong>Total Games:</strong> ${pongStats.total_games}</p>
            <p class="h5"><strong>Average Score:</strong> ${pongStats.average_score}</p>
            <p class="h5"><strong>Total Playtime:</strong> ${pongStats.playtime}</p>
        </div>

        <div class="col-md-5 card p-4 mx-2 mb-4 shadow-sm">
            <p class="h5"><strong>Win Percentage:</strong> <span class="text-success fw-bold">${pongStats.win_percentage}%</span></p>
            <p class="h5"><strong>Precision:</strong> <span class="text-primary fw-bold">${pongStats.precision}%</span></p>
        </div>

        <div class="col-10 mt-3">
            <p class="mb-2">Win Percentage</p>
            <div class="progress">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${pongStats.win_percentage}%;" aria-valuenow="${pongStats.win_percentage}" aria-valuemin="0" aria-valuemax="100">${pongStats.win_percentage}%</div>
            </div>
        </div>

        <div class="col-10 mt-3">
            <p class="mb-2">Precision</p>
            <div class="progress">
                <div class="progress-bar bg-primary" role="progressbar" style="width: ${pongStats.precision}%;" aria-valuenow="${pongStats.precision}" aria-valuemin="0" aria-valuemax="100">${pongStats.precision}%</div>
            </div>
        </div>
        `;
    }

    return document.getElementById('app').innerHTML;
};

function get_friendship_content(friendship_data, user_id) {
    // yourself: 0, not friend: 1, friend: 2, pending request: 3, request received: 4
    if (friendship_data.status === 2) {
        return `
            <p>You are friend already !</p>
            <button class="btn btn-outline-danger" id="remove-friend" data-relation-id=${friendship_data.id}>Remove Friend</button>
        `;
    } else if (friendship_data.status === 1) {
        return `
            <p>You are not friend !</p>
            <button class="btn btn-outline-success" id="add-friend" data-user-id=${user_id}>Add Friend</button>
        `;
    } else if (friendship_data.status === 3) {
        return `
            <p>You sent them a friend request !</p>
            <button class="btn btn-outline-danger" id="cancel-request" data-relation-id=${friendship_data.id}>Cancel Request</button>
        `;
    } else if (friendship_data.status === 4) {
        return `
            <p>They sen\'t you a friend request !</p>
            <button class="btn btn-outline-success accept-request" id="accept-request" data-relation-id=${friendship_data.id}>Accept</button>
            <button class="btn btn-outline-danger decline-request" id="decline-request" data-relation-id=${friendship_data.id}>Decline</button>
        `;
    } else {
        return '<p>Your profile</p>';
    }
}

document.addEventListener("click", e => {
    const link = e.target.closest("a[data-link]");
    if (link) {
        e.preventDefault();
        navigateTo(link.href);
    }
});

window.addEventListener("popstate", router);

document.addEventListener("DOMContentLoaded", router);

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", async (event) => {
        if (event.target.matches("#accept-request-list")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleAcceptRequest(relationId);
        }

        if (event.target.matches("#decline-request-list")) {
            event.preventDefault();
            const relationId = event.target.getAttribute('data-relation-id');
            await handleDeclineRequest(relationId);
        }

    });
});

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

    if (response.ok) {
        await Friends();
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

    if (response.ok) {
        await Friends();
    } else {
        alert('Failed to decline the request.');
    }
}