// router.js

// Function to navigate to a new URL and update content
const navigateTo = url => {
    history.pushState(null, null, url);
    router();
};

// Router function to handle routes
const router = async () => {
    const routes = [
        { path: "/", view: Home },
        { path: "/games", view: Games },
        { path: "/profile", view: Profile },
        { path: "/settings", view: Settings }
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
        <p>Welcome to ft_transcendance!</p>
    </div>
`;

const Games = () => `
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
    </div>
`;

const Settings = () => `
    <div class="text-center">
        <h1>Settings Page</h1>
        <p>Customize your settings.</p>
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
