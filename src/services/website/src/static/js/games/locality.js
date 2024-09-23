// TODO: from quick game we either select LOCAL or ONLINE -> LocalQuickGameState
class GameLocality {
	constructor(context, game, prevState, localGame, onlineGame) {
		this.prevState = prevState;
		this.localGameState = localGame;
		this.onlineGameState = onlineGame;
		this.localButton = document.createElement('button');
		this.localButton.textContent = 'Local';
		this.localButton.className = "btn btn-outline-light mb-2 w-100 h-100";
		this.onlineButton = document.createElement('button');
		this.onlineButton.textContent = 'Online';
		this.onlineButton.className = "btn btn-outline-light mb-2 w-100 h-100";
		this.localButton.addEventListener('click', () => this.localGame())
		this.onlineButton.addEventListener('click', () => this.onlineGame())
		this.context = context;
	};

	execute() {
		this.context.gameMenu.style.display = 'block';
		this.context.gameMenuHeader.textContent = 'Multiplayer Mode';
		this.context.gameMenuBody.innerHTML = '';
		this.context.gameMenuBody.appendChild(this.localButton);
		this.context.gameMenuBody.appendChild(this.onlineButton);
		this.context.gameMenuFooter.innerHTML = `
		<div class="d-flex flex-row align-items-center mt-2">
			<button type="button" id="backButton" class="btn btn-outline-light mx-2">Back</button>
		</div>`;
		const backButton = document.getElementById("backButton");
		backButton.addEventListener('click', () => this.back())

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
