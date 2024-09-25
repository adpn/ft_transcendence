class GameEndedState {
	constructor(game, context, prevState, gameModeState) {
		/* todo: give up buttons bellow the canvas.*/
		this.prevState = prevState;
		this.gameModeState = gameModeState;
		// Replay button
		this.replayButton = this.createReplayButton();
		this.quitButton = this.createQuitButton(); // Optional, similar pattern
		this.context = context;
		this.game = game;
	}
	setMessage(message, is_winner) {
		//todo: set message.
	}

	createReplayButton() {
		const button = document.createElement('button');
		button.textContent = 'Replay';
		button.style.display = 'flex';
		button.className = "btn btn-outline-light mb-2 w-100 h-100";
		button.addEventListener('click', () => this.replay());

		return button;
	}

	createQuitButton() {
		const button = document.createElement('button');
		button.textContent = 'Quit';
		button.style.display = 'flex';
		button.className = "btn btn-outline-light mb-2";
		button.addEventListener('click', () => this.giveUp());

		return button;
	}

	replay() {
		this.context.changeState(this.gameModeState);
	}

	giveUp() {
		this.context.changeState(this.prevState);
	}

	execute() {
		this.game.clear(); // clear what the game uses to display on the canvas
		this.context.gameUI.style.display = 'flex'
		this.context.gameMenu.style.display = 'flex';
		this.context.gameMenuHeader.textContent = 'Game Over';
		this.context.gameMenuBody.innerHTML = ''; // display some message here..
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
		// todo: add player profile on the side of the canvas.
		// need give up button above nicely in the middle between player names, the canvas.
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
			// TODO: handle disconnections etc.
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
		this.context.gameUI.style.display = 'none';
		this.game.load(this.context.canvas);
		this.game.start(this.socket);
	}
}
