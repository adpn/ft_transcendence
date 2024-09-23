class OnlineTournamentGameState {
	constructor(context, game, prevState) {
		this.gameEndState = new GameEndedState(
			game, context, prevState, this);
		this.playingState = new PlayingState(
			game, context, this, this.gameEndState);
		this.game = game;
		this.prevState = prevState;
		this.cancelBtn = document.createElement('button');
		this.cancelBtn.textContent = 'Cancel';
		this.cancelBtn.className = "btn btn-outline-light mb-2 w-100 h-100";

		this.cancelBtn.addEventListener('click', () => this.cancel());
		this.context = context;
	};
	cancel() {
		if (this.socket)
			this.socket.close();
		this.context.loadingOverlay.style.display = 'none';
		this.context.gameUI.style.display = 'flex'
		this.context.state = this.prevState;
		this.context.state.execute();
	}
	execute() {
		//todo launch loading screen and animations.
		// Clear the game menu content
		this.context.gameMenu.style.display = 'none';
		this.context.overlayBody.innerHTML = '';
		this.context.loadingOverlay.style.display = 'flex';
		this.context.overlayBody.appendChild(this.cancelBtn);
		this.joinTournament();
	};

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

	update(data) {
		if (data.type == "end") {
			if (data.status == "lost") {
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
			if (data.status == "win") {
				if (data.context == "round") {
					// move to next round
					// TODO: maybe put a confirmation to move to the next round.
					this.context.gameUI.style.display = 'flex'
					this.context.state = this;
					this.execute();
					return;
				}
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
		}
		else if (data.type == "participant") {
			//new participant joined. -> update view... (fetch user data of the new participant)
			return;
		}
		this.game.update(data);
	}

	joinTournament() {
		// create a game and connect to socket.
		fetch("/games/join_tournament/", {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken"),
				"Authorization": "Bearer " + localStorage.getItem("auth_token")
			},
			credentials: "include",
			body: JSON.stringify({
				"game": this.game.name
			})
		})
			.then((response) => {
				if (!response.ok) {
					throw new Error(response.status);
				}
				return response.json();
			})
			.then(data => {
				this.socket = new WebSocket(`wss://${data.ip_address}/ws/game/pong/${data.game_room_id}/?csrf_token=${getCookie("csrftoken")}&token=${localStorage.getItem("auth_token")}`);
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
			})
			.catch((error) => {
				// stop game_menu animations display error in menu.
				// todo: display error message in the loading window
				// todo: display error message in the loading window
				// then go back game menu.
				this.cancel();
				console.log(error); // maybe display the error message in the window
			});
	}
}
