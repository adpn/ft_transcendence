class ParticipantFormState {
	constructor(context, localTournamentState, num_forms) {
		this.localTournamentState = localTournamentState;
		this.context = context;
		this.startButton = null;
		this.num_forms = num_forms;
	}

	execute() {
		this.render(this.num_forms);
	}

	render(num_players) {
		this.renderForms(num_players);
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="playButton" class="btn btn-outline-light mx-2" disabled>Play</button>
			<button type="button" id="backButton" class="btn btn-outline-light mx-2">Back</button>
		</div>`;
		this.startButton = document.getElementById('playButton');
		const backButton = document.getElementById('backButton');
		this.startButton.addEventListener('click', () => this.addTournamentPlayers());
		backButton.addEventListener('click', () => this.back())
	}

	back() {
		this.context.state = this.localTournamentState;
		this.context.state.execute();
	}

	generateForm(index) {
		return `
		<div class="col col-md-3 justify-content-center">
			<form justify-content-center flex-column room-tag">
				<h10 class="text-center">Room ${index + 1}</h10>
				<input type="text" class="form-control player-tag bg-dark text-light flex-column mb-2 white-placeholder" id="player1-${index}" placeholder="Player Name">
				<input type="text" class="form-control player-tag bg-dark text-light flex-column white-placeholder" id="player2-${index}" placeholder="Player Name">
			</form>
		</div>`;
	}

	renderForms(number) {
		this.context.gameMenuBody.innerHTML = `
		<div class="row w-100 h-100 justify-content-md-center" id="formsContainer"></div>`;
		const formsContainer = document.getElementById('formsContainer');
		for (let i = 0; i < number; i++) {
			formsContainer.innerHTML += this.generateForm(i);
		}
		// TODO: add function to fetch once the player has been added
		this.addInputListeners();  // Re-add listeners to the input fields
	}

	addInputListeners() {
		const inputs = document.querySelectorAll('.player-tag');
		inputs.forEach(input => {
			input.addEventListener('input', () => this.checkFormCompletion());
		});
	}

	checkFormCompletion() {
		const inputs = document.querySelectorAll('.player-tag');
		const values = Array.from(inputs).map(input => input.value.trim());

		// Check if all inputs are filled
		const allFilled = values.every(value => value !== '');

		// Find duplicate values
		const duplicates = values
			.filter((value, index, self) => self.indexOf(value) !== index && value !== '');

		// Highlight the duplicates and remove highlights from non-duplicates
		inputs.forEach(input => {
			if (duplicates.includes(input.value.trim())) {
				input.classList.add('duplicate');
			} else {
				input.classList.remove('duplicate');
			}
		});

		this.startButton.disabled = !(allFilled && allUnique);
	}

	async addTournamentPlayers() {
		await this.localTournamentState.createTournament(this.num_players);
		const promises = Array.from(inputs).map(input => {
			return joinTournament(input.value.trim()).catch(error => {
				console.error(`Error for input ${input.value}:`, error);
				return null; // Return null or any fallback value in case of error
			});
		});
		try {
			const results = await Promise.all(promises);
			console.log('All joinTournament requests handled:', results);
		} 
		catch (error) {
			console.error('An unexpected error occurred:', error);
		}
		await this.localTournamentState.nextRoom();
	}
}

class LocalTournamentGameState {
	constructor(context, game, prevState) {
		this.buttonGrid = new CustomGrid(context, 4);
		this.context = context;
		this.game = game;
		this.endGameState = new GameEndedState(
			game, context, prevState, this)
		this.playingState = new PlayingState(
			game, context, this, this.endGameState);
		this.currentRound = 0;
		this.tournament = null;
	}

	async addTournamentPlayer(player_name) {
		const response = await fetch("/games/join_tournament/", {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken"),
				"Authorization": "Bearer " + localStorage.getItem("auth_token")
			},
			credentials: "include",
			body: JSON.stringify({
				"game": this.game.name,
				"mode": "local",
				"guest_name": player_name
			})
		});

		if (!response.ok) {
			throw new Error(`Error ${response.status}: Failed to create game`);
		};
	}

	async createTournament(max_players) {
		const response = await fetch("/games/create_tournament/", {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken"),
				"Authorization": "Bearer " + localStorage.getItem("auth_token")
			},
			credentials: "include",
			body: JSON.stringify({
				"game": this.game.name,
				"max_players": max_players,
				"mode": "local"
			})
		});
		if (!response.ok) {
			throw new Error(`Error ${response.status}: Failed to create tournament`);
		}
		this.tournament = await response.json();
	}

	handleEvent(event) {
		if (JSON.parse(event.data).status == "ready") {
			// TODO: check if game already started.
			this.context.loadingOverlay.style.display = 'none';
			this.context.gameUI.style.display = 'none';
			this.context.changeState(this.playingState);
			this.game.start(this.socket);
		}
	}

	startGame(data) {
		this.socket = new WebSocket(`wss://${data.ip_address}/ws/game/pong/${data.game_room_id}/?csrf_token=${getCookie("csrftoken")}&token=${localStorage.getItem("auth_token")}&local=true&player1=${data.player1}&player2=${data.player2}`);
		if (this.socket.readyState > this.socket.OPEN) {
			// todo: display error message in the loading window.
			// this.cancel();
			throw new Error("WebSocket error: " + this.socket.readyState);
		}
		this.socket.addEventListener("open", () => {
			this.playingState.bindSocket(this.socket);
			this.socket.addEventListener("message", (event) => {
				this.handleEvent(event);
			});
		});
	}

	async nextRoom() {
		// plays the next room
		const response = await fetch("/games/get_tournament_room/", {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken"),
				"Authorization": "Bearer " + localStorage.getItem("auth_token")
			},
			credentials: "include",
			body: JSON.stringify({
				"tournament_id": this.tournament.id,
				"round": this.currentRound,
				"active": true
			})
		});
		if (response.status == 200 || response.status == 201) {
			//todo: connect to a new room.
			//TODO: show next round display.
			const room = await response.json();
			this.startGame(room);
			this.context.changeState(this.playingState);
			return
		}
		else if (response.status == 404) {
			// try to move to the next round.
			this.currentRound++;
			return await this.nextRoom();
		}
		throw new Error(`Error ${response.status}: Failed to start tournament`);
	}

	update(data) {
		if (data.type == "end") {
			if (data.status == "lost") {
				this.gameStatus = "ended";
				// todo: display winner.
				if (this.gameStatus == "win")
					//this.gameEndState.setWinner(data.winner);
					this.gameEndState.setMessage("You Won!", true);
				else
					this.gameEndState.setMessage("You Lost!", false);
				this.context.changeState(this.gameEndState);
				return;
			}
			if (data.status == "win") {
				if (data.context == "round") {
					// move to next room or to next round.
					this.nextRoom();
					return;
				}
				this.gameStatus = "ended";
				if (this.gameStatus == "win")
					this.gameEndState.setMessage("You Won!", true);
				else
					this.gameEndState.setMessage("You Lost!", false);
				this.context.changeState(this.gameEndState);
				return;
			}
		}
		this.game.update(data);
	}

	moveToForms(num_players) {
		const state = new ParticipantFormState(
			this.context,
			this,
			num_players
		)
		this.context.state = state;
		state.execute();
	}

	generateButton(name) {
		return `
			<button type="button" id="${name}Button" class="btn btn-outline-light w-100 h-100">${name}</button>
		`;
	}

	execute() {
		this.context.gameMenu.style.display = 'flex';
		this.context.gameMenuHeader.textContent = `${this.game.name.toUpperCase()} LOCAL TOURNAMENT`;
		this.buttonGrid.render();
		this.buttonGrid.addHTMLElement(this.generateButton("4 Players"));
		this.buttonGrid.addHTMLElement(this.generateButton("8 Players"));
		this.buttonGrid.addHTMLElement(this.generateButton("16 Players"));
		const button1 = document.getElementById("4 PlayersButton");
		button1.addEventListener('click', () => this.moveToForms(4));
		const button2 = document.getElementById("8 PlayersButton");
		button2.addEventListener('click', () => this.moveToForms(8));
		const button3 = document.getElementById("16 PlayersButton");
		button3.addEventListener('click', () => this.moveToForms(16));
	}
}
