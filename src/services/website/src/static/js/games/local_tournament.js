class ParticipantFormState {
	constructor(context, local_tournament_state, num_forms) {
		this.local_tournament_state = local_tournament_state;
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
		<div class="row w-100 h-100 justify-content-md-center" id="formsContainer"></div>`;
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
		// todo: once a form has been filled, make a pull request. to check if it is valid -> the server will reject
		// any duplicate names
		const inputs = document.querySelectorAll('.player-tag');
		const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
		this.startButton.disabled = !allFilled;
	}
}

class CustomGrid {
	constructor(context, col_size) {
		this.context = context;
		this.col_size = col_size;
	}

	render() {
		this.context.gameMenuBody.innerHTML = `
		<div class="row w-100 h-100 justify-content-md-center" id="customGridContainer"></div>`;
	}

	addHTMLElement(value) {
		const container = document.getElementById("customGridContainer");
		container.innerHTML += this.generateColumn(value);
	}

	generateColumn(value) {
		return `
		<div class="col col-md-${this.col_size} justify-content-center">
			<div class="justify-content-center flex-column w-100 h-100">
				${value}
			</div>
		</div>`;
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
		this.participantsState = new ParticipantFormState(
			context, this)
		this.buttonGrid = new CustomGrid(context, 4);
		this.context = context;
	}

	startTournament() {
		// todo: at each end of game, fetch game rooms with players that are not eliminated.
		// if the're no more rooms, move to the next round -> do this until there is a win condition.
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
		// TODO: fetch possible players.
		// add buttons for selecting one of the possible number of players.
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