// router.js

// Function to navigate to a new URL and update content
export const navigateTo = async url => {
    history.pushState(null, null, url);
    await router();
    const matches = url.match('https://[^/]*/');
    if (matches && matches.length) {
        window.dispatchEvent(new Event(url.substr(matches[0].length)));
    }
};

// Router function to handle routes
const router = async () => {
    const routes = [
        { path: "/", view: Home },
        { path: "/pong", view: Pong },
        { path: "/other-game", view: Other_game },
        { path: "/profile", view: Profile },
        { path: "/friends", view: Friends },
        { path: "/stats", view: Stats }
    ];

    // Find a matching route or return 404
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: location.pathname === route.path
        };
    });

    let match = potentialMatches.find(potentialMatch => potentialMatch.isMatch);

    if (!match) {
        match = {
            route: { path: "/404", view: () => "<h1>404 - Page Not Found</h1>" },
            isMatch: true
        };
    }

    // Render the view
    document.getElementById('app').innerHTML = await match.route.view();
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
        <div class="col text-center">
            <div class="canvas-container">
                <canvas id="gameCanvas" class="w-100 border"></canvas>
            </div>
        </div>
        <div id="game-button">
        </div>
    </div>
`;

const Other_game = () => `
    <div class="row">
    <div class="col text-center">
        <div class="canvas-container">
            <canvas id="gameCanvas" class="w-100 border"></canvas>
        </div>
    </div>
    </div>
`;

const Profile = async () => {
    const token = localStorage.getItem('jwt');
    const response = await fetch('/auth/is_authenticated/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
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
        <h1>Profile Page</h1>
        <p>Manage your profile here.</p>

        <!-- Change Profile Picture -->
        <div id="profile-picture-change" class="mb-3">
            <h4>Change Profile Picture</h4>
            <form id="profile-picture-form" enctype="multipart/form-data">
                <img src="${profile_picture}" alt="Profile Picture" width="100" height="100">
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

const Friends = () => `
    <div class="text-center">
        <h1>Friends Page</h1>
        <div id="friends-invites">
            <span> temporary friends invites </span>
        </div>
        <div id="friends-list">
            <span> temporary friends list </span>
        </div>
    </div>
`;

const Stats = async () => {
    const token = localStorage.getItem('jwt');
    const response = await fetch('/auth/is_authenticated/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
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

    const statsResponse = await fetch('/stats/personal_stats/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    const statsData = await statsResponse.json();
    if (statsData.total_games === 0) {
        document.getElementById('app').innerHTML = `
        <div class="text-center">
            <h1>Stats Page</h1>
            <p>No games played yet.</p>
        </div>
        `;
    } else {
        document.getElementById("total-stats-content").textContent =
            `Total Games: ${statsData.total_games} | Wins: ${statsData.total_wins} | Losses: ${statsData.total_losses}`;

        const gameHistoryList = document.getElementById("game-history-list");
        gameHistoryList.innerHTML = '';

        statsData.games.forEach(game => {
            const listItem = document.createElement("div");
            listItem.className = `game-stat ${game.is_winner ? 'victory' : 'defeat'}`;

            const resultText = game.is_winner ? 'Victory' : 'Defeat';
            listItem.innerHTML = `
                <strong>${resultText}</strong> -
                Opponent: ${game.opponent} |
                Your Score: ${game.personal_score} |
                Opponent's Score: ${game.opponent_score} |
                Duration: ${game.game_duration} |
                Date: ${new Date(game.game_date).toLocaleString()}
            `;

            gameHistoryList.appendChild(listItem);
        });
    }
    return document.getElementById('app').innerHTML;
};

document.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
        e.preventDefault();
        navigateTo(e.target.href);
    }
});

window.addEventListener("popstate", router);

document.addEventListener("DOMContentLoaded", router);
