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
