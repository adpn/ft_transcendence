// TODO: from quick game we either select LOCAL or ONLINE -> LocalQuickGameState
class GameLocality {
	constructor(context, game, prevState, localGame, onlineGame) {
		this.prevState = prevState;
		this.localGameState = localGame;
		this.onlineGameState = onlineGame;
		this.context = context;
		this.localityModes = new CustomGrid(context, 6);
		this.game = game;
	};

	execute() {
		this.context.gameMenu.style.display = 'flex';
		this.localityModes.render();
		this.context.gameMenuHeader.textContent = `${this.game.name.toUpperCase()} MULTIPLAYER MODE`;
		this.localityModes.addHTMLElement(`<button type="button" id="localButton" class="btn btn-outline-light w-100 h-100">Local Game</button>`);
		this.localityModes.addHTMLElement(`<button type="button" id="onlineButton" class="btn btn-outline-light w-100 h-100">Online Game</button>`);
		// this.context.gameMenuBody.innerHTML = '';
		// this.context.gameMenuBody.appendChild(this.localButton);
		// this.context.gameMenuBody.appendChild(this.onlineButton);
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="backButton" class="btn btn-outline-light mx-2 w-100">Back</button>
		</div>`;
		const localButton = document.getElementById("localButton");
		const onlineButton = document.getElementById("onlineButton");
		const backButton = document.getElementById("backButton");
		localButton.addEventListener('click', () => this.localGame());
		onlineButton.addEventListener('click', () => this.onlineGame())
		backButton.addEventListener('click', () => this.back());

	};

	back() {
		this.context.state = this.prevState;
		this.context.state.execute();
	}

	localGame() {
		this.context.state = this.localGameState;
		this.context.state.execute()
	}

	onlineGame() {
		this.context.state = this.onlineGameState;
		this.context.state.execute()
	}
}
