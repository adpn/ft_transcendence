class GameEndedState {
	constructor(game, context, prevState, gameModeState) {
		this.prevState = prevState;
		this.gameModeState = gameModeState;
		this.context = context;
		this.game = game;
	}
	setMessage(winner) {
		this.context.gameMenuBody.textContent = "The winner is " + winner;
	}

	replay() {
		this.context.changeState(this.gameModeState);
	}

	giveUp() {
		this.context.changeState(this.prevState);
	}

	execute() {
		this.game.clear();
		this.context.gameUI.style.display = 'flex'
		this.context.gameMenu.style.display = 'flex';
		this.context.gameMenuHeader.textContent = 'Game Over';
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="replayButton" class="btn btn-outline-light mx-2">Replay</button>
			<button type="button" id="quitButton" class="btn btn-outline-light mx-2">Back</button>
		</div>
		`;

		const replay_button = document.getElementById("replayButton");
		const quit_button = document.getElementById("quitButton");
		replay_button.addEventListener('click', () => this.replay());
		quit_button.addEventListener('click', () => this.giveUp());

	}
}

class PlayingState {
	constructor(game, context, gameMode, gameEndState) {
		this.gameMode = gameMode;
		this.socket = null;
		this.gameStatus = "playing"
		this.gameEndState = gameEndState;
		this.game = game;
		this.context = context;
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
			this.gameMode.update(received_data)
			return;
		}
		this.gameMode.update(received_data);
	}

	disconnected() {
		if (this.gameStatus != "ended") {
			// if the game did not end after disconnection, stay in playing state.
			return;
		}
	}

	execute() {
		this.game.clear();
		this.context.gameUI.style.display = 'none';
		this.context.canvas = null;
		this.context.canvas = document.getElementById("gameCanvas" + this.game.canvas_context);
		this.context.canvas.style.display = 'flex';
		this.game.load(this.context.canvas);
		this.game.start(this.socket);
	}
}
