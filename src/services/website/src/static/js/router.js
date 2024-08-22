// router.js

// Function to navigate to a new URL and update content
const navigateTo = async url => {
    history.pushState(null, null, url);
    await router();
    window.dispatchEvent(new Event(url));
};

// Router function to handle routes
const router = async () => {
    const routes = [
        { path: "/", view: Home },
        { path: "/pong", view: Pong },
        { path: "/other-game", view: Other_game },
        { path: "/profile", view: Profile },
        // { path: "/settings", view: Settings },
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

const Profile = () => `
    <div class="text-center">
        <h1>Profile Page</h1>
        <p>Manage your profile here.</p>
        <div id="profile-picture-change">
            <span> temporary profile picture change </span>
        </div>
        <div id="username-change">
            <span> temporary username change </span>
        </div>
        <div id="password-change">
            <span> temporary password change </span>
        </div>
    </div>
`;

// const Settings = () => `
//     <div class="text-center">
//         <h1>Settings Page</h1>
//         <p>Customize your settings.</p>
//     </div>
// `;

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

const Stats = () => `
    <div class="text-center">
        <h1>Stats Page</h1>
        <div id="total-stats">
            <span> temporary total stats </span>
        </div>
        <div id="game-history">
            <span> temporary game history (will use json) </span>
        </div>
    </div>
`;

// Event delegation for navigation links
document.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
        e.preventDefault();
        navigateTo(e.target.href);
    }
});

// Handle popstate event (Back/Forward buttons)
window.addEventListener("popstate", router);

// Initial load
document.addEventListener("DOMContentLoaded", router);
