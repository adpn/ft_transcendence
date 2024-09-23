document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("game", load_games)
});

var gameMenu;
var canvas;
var loadingOverlay;
var gameUI;
let state = null;
var overlayBody;
var gameMenuBody;
var gameMenuHeader;
var gameMenuFooter;

var games_context = {
	canvas: null,
	loadingOverlay: null,
	overlayBody: null,
	gameMenu: null,
	gameUI: null,
	gameMenuHeader: null,
	gameMenuBody: null,
	gameMenuFooter: null,
	state: null,
	changeState: function (state) {
		this.state = state;
		state.execute();
	}
}

class GameModes {
	constructor(context, game, prevState) {
		this.game = game
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

		this.prevState = prevState;
		this.context = context;
		this.modesGrid = new CustomGrid(context, 6);
	};
	goBack() {
		this.changeState(this.prevState);
	}
	joinTournament() {
		this.context.changeState(this.tournamentState);
	}
	quickGame() {
		this.context.changeState(this.quickGameState);
	}
	execute() {
		this.context.gameMenu.style.display = 'flex';
		this.modesGrid.render();
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
		backButton.addEventListener('click', () => this.goBack())
	}
}

class GameMenu {
	constructor(context) {
		this.pongState = new GameModes(context, Pong, this);
		this.context = context;
		this.gamesGrid = new CustomGrid(context, 6);
	};

	launchGame(game) {
		if (game == "pong") {
			this.context.state = this.pongState;
			this.context.state.execute()
		}
		else if (game == "snake") {
			console.log("SNAKE ?! SNAAAAAAAAAAAKE !!!")
		}
	}

	execute() {
		this.context.gameMenu.style.display = 'flex';
		this.gamesGrid.render();
		this.context.gameMenuHeader.textContent = 'CHOOSE GAME';
		this.gamesGrid.addHTMLElement(`<button type="button" id="pongButton" class="btn btn-outline-light w-100 h-100">Pong</button>`);
		this.gamesGrid.addHTMLElement(`<button type="button" id="snakeButton" class="btn btn-outline-light w-100 h-100">Snake</button>`);
		const pongButton = document.getElementById("pongButton");
		const snakeButton = document.getElementById("snakeButton");
		pongButton.addEventListener('click', () => this.launchGame("pong"));
		snakeButton.addEventListener('click', () => this.launchGame("snake"));
		this.context.gameMenuFooter.innerHTML = '';
	}
}

function load_games() {
	games_context.canvas = document.getElementById("gameCanvas");
	games_context.gameMenu = document.getElementById('game-menu');
	games_context.gameMenu.style.display = 'none';
	games_context.gameMenuHeader = document.getElementById("game-menu-header");
	games_context.gameMenuBody = document.getElementById("game-menu-body");
	games_context.gameMenuFooter = document.getElementById("game-menu-footer");
	games_context.loadingOverlay = document.getElementById('loading-overlay');
	games_context.overlayBody = document.getElementById('overlay-body');
	games_context.gameUI = document.getElementById('game-ui');
	// todo: check if the user is signed-in first ?
	if (games_context.state == null)
		games_context.state = new GameMenu(games_context);
	games_context.state.execute();
}
