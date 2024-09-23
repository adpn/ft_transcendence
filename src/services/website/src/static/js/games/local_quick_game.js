/*
	TODO: in local mode, need an interface to set guest players names.
	in local mode, we make two create_game fetches (one per player)
	then connect to a single room.
*/
class LocalQuickGameState {
	constructor(context, game, prevState) {
		this.gameEndState = new GameEndedState(game, context, prevState, this);
		this.playingState = new PlayingState(game, context, this, this.gameEndState);
		this.game = game;
		this.prevState = prevState;
		this.context = context;
	}

	update(data) {
		// todo: move to result state
		if (data.type == "end") {
			this.gameStatus = "ended";
			if (this.gameStatus == "win")
				this.gameEndState.setMessage("You Won!", true);
			else
				this.gameEndState.setMessage("You Lost!", false);
			if (this.socket)
				this.socket.close();
			this.context.state = this.gameEndState;
			this.context.state.execute();
			return;
		}
		this.game.update(data);
	}

	handleEvent(event) {
		if (JSON.parse(event.data).status == "ready") {
			// todo: if a player was found, display his profile and move to PlayingState.
			// move to playing state.
			// todo: wait for players to be ready. (click on button?)
			// this.loadingModal.hide();
			this.context.loadingOverlay.style.display = 'none';
			this.context.gameUI.style.display = 'none';
			this.context.state = this.playingState;
			this.context.state.execute();
			this.game.start(this.socket);
		}
	}

	async startGame(player1, player2) {
		try {
			const response1 = await fetch("/games/create_game/", {
				method: "POST",
				headers: {
					"X-CSRFToken": getCookie("csrftoken"),
					"Authorization": "Bearer " + localStorage.getItem("auth_token")
				},
				credentials: "include",
				body: JSON.stringify({
					"game": this.game.name,
					"mode": "local",
					"guest_name": player1
				})
			});

			if (!response1.ok) {
				throw new Error(`Error ${response1.status}: Failed to create game`);
			}

			const response2 = await fetch("/games/create_game/", {
				method: "POST",
				headers: {
					"X-CSRFToken": getCookie("csrftoken"),
					"Authorization": "Bearer " + localStorage.getItem("auth_token")
				},
				credentials: "include",
				body: JSON.stringify({
					"game": this.game.name,
					"mode": "local",
					"guest_name": player2
				})
			});

			if (!response2.ok) {
				throw new Error(`Error ${response2.status}: Failed to create game`);
			}

			const data = await response2.json();
			// make a single connection for both players.
			this.socket = new WebSocket(`wss://${data.ip_address}/ws/game/pong/${data.game_room_id}/?csrf_token=${getCookie("csrftoken")}&token=${localStorage.getItem("auth_token")}&local=true&player1=${player1}&player2=${player2}`);
			if (this.socket.readyState > this.socket.OPEN) {
				// todo: display error message in the loading window.
				this.cancel();
				throw new Error("WebSocket error: " + this.socket.readyState);
			}
			this.socket.addEventListener("open", () => {
				this.playingState.bindSocket(this.socket);
				this.socket.addEventListener("message", (event) => {
					this.handleEvent(event);
				});
			});
		}
		catch (error) {
			// stop game_menu animations display error in menu.
			// todo: display error message in the loading window
			// todo: display error message in the loading window
			// then go back game menu.
			this.cancel();
			// resizeCanvas();
			console.log(error); // maybe display the error message in the window
		}
	}

	cancel() {
		this.context.state = this.prevState;
		this.context.state.execute();
	}

	execute() {
		this.context.gameMenu.style.display = 'block';
		this.context.gameMenuHeader.textContent = `${this.game.name.toUpperCase()} LOCAL QUICK GAME`;
		this.context.gameMenuBody.innerHTML = `
		<form id="playerForm" class="d-flex flex-column justify-content-center">
			<h10 class="text-center mb-2">Room</h10>
			<input type="text" class="form-control custom-input text-light mb-2" id="player1" placeholder="Player 1 Name" required>
			<input type="text" class="form-control custom-input text-light" id="player2" placeholder="Player 2 Name" required>
		</form>`;
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row justify-content-center align-items-center">
			<button type="button" id="playButton" class="btn btn-outline-light mx-2 w-100" disabled>Play</button>
			<button type="button" id="backButton" class="btn btn-outline-light w-100">Back</button>
		</div>
		`;
		// const grid = document.getElementById('game-room-grid');
		// grid.innerHTML += gameRoomForm;
		// grid.innerHTML += gameRoomForm;

		const player1Input = document.getElementById('player1');
		const player2Input = document.getElementById('player2');
		const playButton = document.getElementById('playButton');
		const backButton = document.getElementById('backButton');

		function checkPlayers() {
			if (player1Input.value.trim() !== '' && player2Input.value.trim() !== '') {
				playButton.disabled = false;
			}
			else {
				playButton.disabled = true;
			}
		}

		player1Input.addEventListener('input', checkPlayers);
		player2Input.addEventListener('input', checkPlayers);

		playButton.addEventListener('click', async () => {
			const player1 = player1Input.value.trim();
			const player2 = player2Input.value.trim();

			if (player1 && player2) {
				await this.startGame(player1, player2);
			}
		});
		backButton.addEventListener('click', () => this.cancel())
	}
}