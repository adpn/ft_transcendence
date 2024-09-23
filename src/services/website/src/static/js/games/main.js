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
	state: null
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

		this.quickGameBtn = document.createElement('button');
		this.quickGameBtn.textContent = 'Quick Game';
		this.quickGameBtn.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.quickGameBtn.addEventListener('click', () => this.quickGame());

		this.tournamentBtn = document.createElement('button');
		this.tournamentBtn.textContent = 'Tournament';
		this.tournamentBtn.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.tournamentBtn.addEventListener('click', () => this.joinTournament());

		this.backBtn = document.createElement('button');
		this.backBtn.textContent = 'Back';
		this.backBtn.className = "btn btn-outline-light mb-2";

		this.backBtn.addEventListener('click', () => this.goBack());
		this.context = context;


	};
	goBack() {
		this.context.state = this.prevState;
		this.context.state.execute();
	}
	joinTournament() {
		this.context.state = this.tournamentState;
		this.context.state.execute();
	}
	quickGame() {
		this.context.state = this.quickGameState;
		this.context.state.execute();
	}
	execute() {
		this.context.gameMenu.style.display = 'block';
		this.context.gameMenuHeader.textContent = 'Game Mode';
		this.context.gameMenuBody.innerHTML = '';
		this.context.gameMenuBody.appendChild(this.quickGameBtn);
		this.context.gameMenuBody.appendChild(this.tournamentBtn);
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="backButton" class="btn btn-outline-light mx-2">Back</button>
		</div>`;
		const backButton = document.getElementById("backButton");
		backButton.addEventListener('click', () => this.goBack())
		//this.game.load(this.context.canvas);
	}
}

class GameMenu {
	constructor(context) {
		this.pongState = new GameModes(context, Pong, this);
		this.pongButton = document.createElement('button');
		this.pongButton.textContent = 'Pong';
		this.pongButton.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.snakeButton = document.createElement('button');
		this.snakeButton.textContent = 'Snake';
		this.snakeButton.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.backButton = document.createElement('button');
		this.backButton.textContent = 'Back';
		this.backButton.className = "btn btn-outline-light mb-2";

		this.pongButton.addEventListener('click', () => this.launch_game("pong"));
		this.snakeButton.addEventListener('click', () => this.launch_game("snake"));
		this.context = context;

	};

	launch_game(game) {
		if (game == "pong") {
			this.context.state = this.pongState;
			this.context.state.execute()
		}
		else if (game == "snake") {
			console.log("SNAKE ?! SNAAAAAAAAAAAKE !!!")
		}
	}

	execute() {
		this.context.gameMenu.style.display = 'block';
		this.context.gameMenuHeader.textContent = 'Game';
		this.context.gameMenuBody.innerHTML = '';
		this.context.gameMenuBody.appendChild(this.pongButton);
		this.context.gameMenuBody.appendChild(this.snakeButton);
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
