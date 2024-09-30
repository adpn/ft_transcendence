import { Pong } from "../pong.js"
import { Pong3d } from "../pong3d.js"
import { Snake } from "../snake.js"

document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("game", load_games)
});

var games_context = {
	playersContainer: null,
	canvas_context: null,
	canvas: null,
	loadingOverlay: null,
	overlayBody: null,
	gameMenu: null,
	gameUI: null,
	gameMenuHeader: null,
	gameMenuBody: null,
	gameMenuFooter: null,
	state: null,
	changeState(state) {
		this.state = state;
		state.execute();
	}
}

class GameModes {
	constructor(context, game, prevState) {
		this.game = game;
		this.prevState = prevState;
		this.context = context;
		this.modesGrid = new CustomGrid(context, 6);

		this.tournamentState = new GameLocality(
			context,
			game, this,
			new LocalTournamentGameState(context, game, this),
			new OnlineTournamentGameState(context, game, this));
		this.quickGameState = new GameLocality(
			context,
			game,
			this,
			new LocalQuickGameState(context, game, this),
			new OnlineQuickGameState(context, game, this));
	};
	goBack() {
		this.context.changeState(this.prevState);
	}
	joinTournament() {
		this.context.changeState(this.tournamentState);
	}
	quickGame() {
		this.context.changeState(this.quickGameState);
	}
	execute() {
		this.context.canvas = document.getElementById("gameCanvas" + this.game.canvas_context);
		this.context.gameUI.style.display = 'flex';
		this.context.gameMenu.style.display = 'flex';
		this.modesGrid.render(this.context.gameMenuBody);
		this.context.gameMenuHeader.textContent = `${this.game.name.toUpperCase()} GAME MODE`;
		this.modesGrid.addHTMLElement(`<button type="button" id="quickGameButton" class="btn btn-outline-light w-100 h-100">Quick Game</button>`);
		this.modesGrid.addHTMLElement(`<button type="button" id="tournamentButton" class="btn btn-outline-light w-100 h-100">Tournament</button>`);
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="backButton" class="btn btn-outline-light mx-2 w-100">Back</button>
		</div>`;
		const quickGameButton = document.getElementById("quickGameButton");
		const tournamentButton = document.getElementById("tournamentButton");
		const backButton = document.getElementById("backButton");
		quickGameButton.addEventListener('click', () => this.quickGame());
		tournamentButton.addEventListener('click', () => this.joinTournament());
		backButton.addEventListener('click', () => this.goBack());
	}
}

class GameMenu {
	constructor(context) {
		this.pongState = new GameModes(context, Pong, this);
		this.pongButton = document.createElement('button');
		this.pongButton.textContent = 'Pong';
		this.pongButton.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.pong3dState = new GameModes(context, Pong3d, this);
		this.pong3dButton = document.createElement('button');
		this.pong3dButton.textContent = 'Pong 3D';
		this.pong3dButton.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.snakeState = new GameModes(context, Snake, this);
		this.snakeButton = document.createElement('button');
		this.snakeButton.textContent = 'Snake';
		this.snakeButton.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.backButton = document.createElement('button');
		this.backButton.textContent = 'Back';
		this.backButton.className = "btn btn-outline-light mb-2";

		this.pongButton.addEventListener('click', () => this.launch_game("pong"));
		this.pong3dButton.addEventListener('click', () => this.launch_game("pong3d"));
		this.snakeButton.addEventListener('click', () => this.launch_game("snake"));
		this.context = context;
		this.gamesGrid = new CustomGrid(context, 4);
	};

	launchGame(game) {
		if (game == "pong") {
			this.context.state = this.pongState;
			this.context.state.execute();
		}
		else if (game == "pong3d") {
			this.context.state = this.pong3dState;
			this.context.state.execute();
		}
		else if (game == "snake") {
			this.context.state = this.snakeState;
			this.context.state.execute();
		}
	}

	execute() {
		// if not logged in exeCUTE ErorrState instead
		this.context.gameMenu.style.display = 'flex';
		this.gamesGrid.render(this.context.gameMenuBody);
		this.context.gameMenuHeader.textContent = 'CHOOSE GAME';
		this.gamesGrid.addHTMLElement(`<button type="button" id="pongButton" class= "btn btn-outline-light w-100 h-100">Pong</button>`);
		this.gamesGrid.addHTMLElement(`<button type="button" id="pong3dButton" class= "btn btn-outline-light w-100 h-100">Pong 3D</button>`);
		this.gamesGrid.addHTMLElement(`<button type="button" id="snakeButton" class="btn btn-outline-light w-100 h-100">Snake</button>`);
		const pongButton = document.getElementById("pongButton");
		const pong3dButton = document.getElementById("pong3dButton");
		const snakeButton = document.getElementById("snakeButton");
		pongButton.addEventListener('click', () => this.launchGame("pong"));
		pong3dButton.addEventListener('click', () => this.launchGame("pong3d"));
		snakeButton.addEventListener('click', () => this.launchGame("snake"));
		this.context.gameMenuFooter.innerHTML = '';
	}
}

function reset_games() {
	games_context.state = new GameMenu(games_context)
}

document.addEventListener(
	"logout",
	reset_games);

function load_games() {
	games_context.gameUI = document.getElementById('game-ui');
	if (!games_context.gameUI)
		return;
	games_context.gameMenu = document.getElementById('game-menu');
	if (!games_context.gameMenu)
		return;
	games_context.players = new PlayersGrid(
		this, document.getElementById('playersContainer'), 2);
	games_context.players.render();
	games_context.gameMenu.style.display = 'none';
	games_context.gameMenuHeader = document.getElementById("game-menu-header");
	games_context.gameMenuBody = document.getElementById("game-menu-body");
	games_context.gameMenuFooter = document.getElementById("game-menu-footer");
	games_context.loadingOverlay = document.getElementById('loading-overlay');
	games_context.overlayBody = document.getElementById('overlay-body');
	games_context.gameUI = document.getElementById('game-ui');
	document.getElementById('gameCanvas2D').style.display = "none";
	document.getElementById('gameCanvas3D').style.display = "none";
	if (games_context.state == null)
		games_context.state = new GameMenu(games_context);
	games_context.state.execute();
}
