class LocalTournamentParticipantsState {
	constructor(context, local_tournament_state) {
		this.local_tournament_state = local_tournament_state;
		this.context = context;
		this.startButton = null;
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
		this.startButton.addEventListener('click', () => this.local_tournament_state.startTournament());
		backButton.addEventListener('click', () => this.back())
	}

	back() {
		this.context.state = this.local_tournament_state;
		this.context.state.execute();
	}

	generateForm(index) {
		return `
		<div class="col col-md-3 justify-content-center">
			<form justify-content-center flex-column">
				<h10 class="text-center">Room ${index + 1}</h10>
				<input type="text" class="form-control player-tag bg-dark text-light flex-column mb-2 white-placeholder" id="player1-${index}" placeholder="Player Name">
				<input type="text" class="form-control player-tag bg-dark text-light flex-column white-placeholder" id="player2-${index}" placeholder="Player Name">
			</form>
		</div>`;
	}

	renderForms(number) {
		this.context.gameMenuBody.innerHTML = `
		<div class="grid-wrapper w-100 h-100 justify-content-md-center">
			<div class="row w-100 h-100" id="formsContainer"></div>
		</div>`;
		const formsContainer = document.getElementById('formsContainer');
		for (let i = 0; i < number; i++) {
			formsContainer.innerHTML += this.generateForm(i);
		}
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
		const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
		this.startButton.disabled = !allFilled;
	}
}

class LocalTournamentGameState {
	constructor(context, game, prevState) {
		// TODO: need an interface for adding players.
		// make a fetch for each participant.
		// make a fetch to get the current participants.
		// make a fetch to get the two next opponents. -> need an api endpoint for this.
		// make a websocket connection by specifying the two opponents.
		// and so on until and "end" condition is met.
		// TODO: have do i retrieve the next game room ?
		// how do i know when to move to the next round?
		// todo: number of players states.
		this.participantsState = new LocalTournamentParticipantsState(context, this)
	}

	startTournament() {
		// todo: at each end of game, fetch game rooms with players that are not eliminated.
		// if the're no more rooms, move to the next round -> do this until there is a win condition.
	}

	execute() {
		// TODO: fetch possible players.
		// add buttons for selecting one of the possible number of players.
		this.participantsState.render(4);
	}
}