document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("game", load_games)
});

var gameMenu;
var canvas;
var loadingOverlay;
var	gameUI;
let	state = null;

class GameEndedState {
	constructor(game, gameModeState, prevState) {
		// todo: 
		// need replay, give up buttons bellow the canvas.
		this.prevState = prevState;
		this.gameModeState = gameModeState;
		this.socket = null;
		// Replay button
		this.replayButton = this.createReplayButton();
		this.giveUpButton = this.createGiveUpButton(); // Optional, similar pattern
	}
	setMessage(message, is_winner) {
		//todo: set message.
	}

	// Method to create the replay button
	createReplayButton() {
		const button = document.createElement('button');
		button.textContent = "Replay";
		button.style.display = 'block';
		button.className = "btn btn-outline-light mb-2";

		// Attach the replay method to the button's click event
		button.addEventListener('click', () => this.replay());

		return button;
	}

	// Optional: Method to create a give-up button
	createGiveUpButton() {
		const button = document.createElement('button');
		button.textContent = "Give Up";
		button.style.display = 'block';
		button.className = "btn btn-outline-light mb-2";

		// Attach the replay method to the button's click event
		button.addEventListener('click', () => this.giveUp());

		return button;
	}

	// Replay method logic
	replay() {
		// go back to either quick game or tournament.
		state = this.prevState;
		state.execute();
	}

	giveUp() {
		state = this.gameModeState;
		state.execute();
	}

	execute() {
		gameUI.style.display = 'flex'
		gameMenu.innerHTML = '';
		gameMenu.style.display = 'block';
		gameMenu.appendChild(this.replayButton);
		gameMenu.appendChild(this.giveUpButton);
	}
}

class PlayingState {
	constructor(game, gameModeState, prevState) {
		// todo: add player profile on the side of the canvas.
		// need cancel, replay, give up buttons bellow the canvas.
		this.prevState = prevState;
		this.gameModeState = gameModeState;
		this.socket = null;
		this.gameStatus = "playing"
		this.gameEndState = new GameEndedState(game, gameModeState, prevState);
	}
	bindSocket(socket) {
		this.socket = socket;
		socket.addEventListener("close", () => this.disconnected());
		socket.addEventListener("message", (event) => this.update(event));
	}
	unbindSocket() {
		this.socket = null;
	}

	update(event) {
		var received_data = JSON.parse(event.data);
		if (received_data.type == "end") {
			// todo: move to result state
			this.gameStatus = "ended";
			if (this.gameStatus == "win")
				this.gameEndState.setMessage("You Won!", true);
			else
				this.gameEndState.setMessage("You Lost!", false);
			state = this.gameEndState;
			state.execute();
			return;
		}
		updatePong(event);
	}
	disconnected() {
		if (this.gameStatus != "ended") {
			// if the game did not end after disconnection, stay in playing state.
			return;
		}
	}

	execute() {
		if (this.socket)
		{
			//this.game.start(this.socket);
			// canvas.focus();
		}
		console.log("PLAYING!");
		gameUI.style.display = 'none';
		loadPong(canvas);
	}
}

class QuickGame {
	constructor(game, prevState) {
		this.playingState = new PlayingState(game, prevState, this);

		this.loadingBody = document.getElementById('loading-screen');
		// this.loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'), {
		// 	backdrop: 'static',  // Prevents closing on clicking outside
		// 	keyboard: false      // Prevents closing on pressing the escape key
		// });
		this.game = game;
		this.prevState = prevState;
		this.cancelBtn = document.createElement('button');
		this.cancelBtn.textContent = 'Cancel';
		this.cancelBtn.className = "btn btn-outline-light mb-2";
		this.cancelBtn.addEventListener('click', () => this.cancel());

		this.socket = null;

	};

	cancel() {
		if (this.socket)
			this.socket.close();
		// if (this.loadingModal)
		// 	this.loadingModal.hide();
		loadingOverlay.style.display = 'none';
		gameUI.style.display = 'flex'
		// put the menu back.
		state = this.prevState;
		state.execute();
	}

	execute() {
		// Clear the game menu content
		gameMenu.style.display = 'none';
		// this.loadingBody.appendChild(this.cancelBtn);
		// this.loadingModal.show();
		loadingOverlay.style.display = 'flex';
		loadingOverlay.appendChild(this.cancelBtn);
		this.connectGameRoom();
	};

	waitRoom(event) {
		if (JSON.parse(event.data).status == "ready") {
			// todo: if a player was found, display his profile and move to PlayingState.
			// move to playing state.
			// todo: wait for players to be ready. (click on button?)
			// this.loadingModal.hide();
			loadingOverlay.style.display = 'none';
			state = this.playingState;
			gameUI.style.display = 'none';
			gameStart(this.socket);
			state.execute();
		}
	}

	connectGameRoom() {
		// create a game and connect to socket.
		fetch("/games/create_game/", {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken"),
				"Authorization": "Bearer " + localStorage.getItem("auth_token")
			},
			credentials: "include",
				body: JSON.stringify({
					"game": "pong"
				})
		})
		.then((response) => {
			if(!response.ok) {
				throw new Error(response.status);
			}
			return response.json();
		})
		.then(data => {
			this.socket = new WebSocket("wss://" + data.ip_address + "/ws/game/pong/" +  data.game_room_id + "/?csrf_token=" + getCookie("csrftoken") + "&token=" + localStorage.getItem("auth_token"));
			if (this.socket.readyState > this.socket.OPEN) {
				// todo: display error message in the loading window.
				this.cancel();
				throw new Error("WebSocket error: " + this.socket.readyState);
			}
			this.socket.addEventListener("open", () => {
				this.playingState.bindSocket(this.socket);
				this.socket.addEventListener("message", (event) => {
					this.waitRoom(event);
				});
			});
		})
		.catch((error) => {
			// stop game_menu animations display error in menu.
			// todo: display error message in the loading window
			// todo: display error message in the loading window
			// then go back game menu.
			this.cancel();
			// resizeCanvas();
			console.log("CAUGHT ERROR!!!");
			console.log(error); // maybe display the error message in the window
		});
	}
}

class Tournament {
	constructor(game, prevState)
	{
		this.game = game;
		this.prevState = prevState;
		this.cancelBtn = document.createElement('button');
		this.cancelBtn.textContent = 'Cancel';
		this.cancelBtn.className = "btn btn-outline-light mb-2";

		this.cancelBtn.addEventListener('click', () => this.cancel());
	};
	cancel() {
		state = this.prevState;
		state.execute();
	}
	execute() {
		//todo launch loading screen and animations.
	};
}

class GameModes {
	constructor(game, prevState)
	{
		this.game = game
		this.tournamentState = new Tournament(game, this);
		this.quickGameState = new QuickGame(game, this);

		this.prevState = prevState;

		this.quickGameBtn = document.createElement('button');
		this.quickGameBtn.textContent = 'Quick Game';
		this.quickGameBtn.className = "btn btn-outline-light mb-2";

		this.quickGameBtn.addEventListener('click', () => this.quickGame());

		this.tournamentBtn = document.createElement('button');
		this.tournamentBtn.textContent = 'Tournament';
		this.tournamentBtn.className = "btn btn-outline-light mb-2";

		this.tournamentBtn.addEventListener('click', () => this.joinTournament());

		this.backBtn = document.createElement('button');
		this.backBtn.textContent = 'Back';
		this.backBtn.className = "btn btn-outline-light mb-2";

		this.backBtn.addEventListener('click', () => this.goBack());

	};
	goBack()
	{
		state = this.prevState;
		state.execute();
	}
	joinTournament()
	{
		state = this.tournamentState;
		state.execute();
	}
	quickGame()
	{
		state = this.quickGameState;
		state.execute();
	}
	execute() {
		gameMenu.innerHTML = '';
		gameMenu.style.display = 'block';
		gameMenu.appendChild(this.quickGameBtn);
		gameMenu.appendChild(this.tournamentBtn);
		gameMenu.appendChild(this.backBtn);
		// todo: abstract this away : game.load(canvas);
		loadPong(canvas);
	}
}

class GameMenu {
	constructor()
	{
		this.pongState = new GameModes("pong", this);
		this.pongButton = document.createElement('button');
		this.pongButton.textContent = 'Pong';
		this.pongButton.className = "btn btn-outline-light mb-2";

		this.otherButton = document.createElement('button');
		this.otherButton.textContent = 'Other Game';
		this.otherButton.className = "btn btn-outline-light mb-2";

		this.backButton = document.createElement('button');
		this.backButton.textContent = 'Back';
		this.backButton.className = "btn btn-outline-light mb-2";

		this.pongButton.addEventListener('click', () => this.launch_game("pong"));
		this.otherButton.addEventListener('click', () => this.launch_game("other"));

	};

	launch_game(game) {
		// todo: need to store and previous state...
	
		if (game == "pong")
		{
			state = this.pongState;
			state.execute()
		}
	}

	execute() {
		gameMenu.style.display = 'block';
		gameMenu.innerHTML = '';
		gameMenu.appendChild(this.pongButton);
		gameMenu.appendChild(this.otherButton);
	}
}

function load_games()
{
	canvas = document.getElementById("gameCanvas");
	gameMenu = document.getElementById('game-menu');
	gameMenu.style.display = 'none';
	loadingOverlay = document.getElementById('loading-overlay');
	gameUI = document.getElementById('game-ui');
	// todo: check if the user is signed-in first ?
	if (state == null)
		state = new GameMenu();
	state.execute();
}
