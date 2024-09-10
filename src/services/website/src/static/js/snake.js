const NOT_JOINED = 0;
const CONNECTING = 1;
const PLAYING = 2;
const WON = 3;
const LOST = 4;
const DISCONNECTED = 6;
const ERROR = 7;

const KEY_DOWN = true;
const KEY_UP = false;
const DIR_UP = 0
const DIR_DOWN = 1
const DIR_LEFT = 2
const DIR_RIGHT = 3

var grid_size = [3, 2];
var block_size = 20;
var margins = [100, 50];
var grid;
var colors = [0x000000];
var to_add = [];

var socket;
var canvas;
var ctx;
var is_focus = false;
var game_status = NOT_JOINED;


document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("snake", loadSnake);
});

function loadSnake() {
	canvas = document.getElementById("gameCanvas");
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", function () { is_focus = true; });
	canvas.addEventListener("blur", function () { is_focus = false; });
	ctx = canvas.getContext("2d", { alpha: false });
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);
	if (game_status >= WON)
		game_status = NOT_JOINED;
	changeButton();
	resizeCanvas();
}

function connectGameRoom() {
	fetch("/games/create_game/", {
		method: "POST",
		headers: {
			"X-CSRFToken": getCookie("csrftoken"),
			"Authorization": "Bearer " + localStorage.getItem("auth_token")
		},
		credentials: "include",
			body: JSON.stringify({
				"game": "snake"
			})
	})
	.then((response) => {
		if(!response.ok)
			throw new Error(response.status);
		return response.json();
		})
	.then(data => {
		socket = new WebSocket("wss://" + data.ip_address + "/ws/game/snake/" + data.game_room_id + "/?csrf_token=" + getCookie("csrftoken") + "&token=" + localStorage.getItem("auth_token"));
		if (socket.readyState > socket.OPEN)
			throw new Error("WebSocket error: " + socket.readyState);
		socket.addEventListener("close", disconnected);
		socket.addEventListener("open", function () {
			game_status = CONNECTING;
			resizeCanvas();
			changeButton();
			socket.addEventListener("message", waitRoom);
		});
	})
	.catch((error) => {
		game_status = ERROR
		resizeCanvas();
		console.log(error);
	});
}

function cancel() {
	socket.close();
}

function disconnected() {
	if (game_status <= PLAYING)
		game_status = DISCONNECTED;
	resizeCanvas();
	changeButton();
}

function waitRoom(e) {
	if (JSON.parse(e.data).status != "ready")
		return ;
	gameStart();
}

function changeButton() {
	switch (game_status) {
		case NOT_JOINED:
		case WON:
		case LOST:
		case DISCONNECTED:
			var title = "find game";
			var btn_class = "success";
			break ;
		case CONNECTING:
			var title = "cancel";
			var btn_class = "danger";
			break ;
		case PLAYING:
			var title = "give up";
			var btn_class = "warning";
	}
	document.getElementById("game-button-container").innerHTML = `
		<button class="btn btn-${btn_class} me-2" id="game-button" type="button">${title}</button>
`;
	var button = document.getElementById("game-button");
	switch (game_status) {
		case NOT_JOINED:
		case WON:
		case LOST:
		case DISCONNECTED:
			button.addEventListener("click", connectGameRoom);
			break ;
		case CONNECTING:
			button.addEventListener("click", cancel);
			break ;
		case PLAYING:
			button.addEventListener("click", GiveUp);
	}
}

function takeInputDown(e) {
	if (!is_focus || e.defaultPrevented) {
		return ;
	}
	submitInput(extractDir(e.key), KEY_DOWN);
	e.preventDefault();
}

function takeInputUp(e) {
	if (!is_focus || e.defaultPrevented) {
		return ;
	}
	submitInput(extractDir(e.key), KEY_UP);
	e.preventDefault();
}

function extractDir(key) {
	switch (key) {
		case "w":
		case "ArrowUp":
			return DIR_UP;
		case "a":
		case "ArrowLeft":
			return DIR_LEFT;
		case "s":
		case "ArrowDown":
			return DIR_DOWN;
		case "d":
		case "ArrowRight":
			return DIR_RIGHT;
	}
}

function resizeCanvas() {
	canvas.width = canvas.scrollWidth;
	canvas.height = canvas.scrollHeight;
	block_size = canvas.width / (grid_size[0] + 4);
	let block_size_y = canvas.height / (grid_size[1] + 6);
	block_size = Math.min(block_size, block_size_y);
	margins[0] = canvas.width - block_size * grid_size[0];
	margins[1] = canvas.height - block_size * grid_size[1];
	switch (game_status) {
		case NOT_JOINED:
			drawMessage("Welcome");
			break ;
		case CONNECTING:
			drawMessage("Connecting...");
			break ;
		case PLAYING:
			drawFrame();
			break ;
		case WON:
			drawMessage("Victory");
			break ;
		case LOST:
			drawMessage("Defeat");
			break ;
		case DISCONNECTED:
			drawMessage("Disconnected");
			break ;
		case ERROR:
			drawMessage("Something went wrong");
	}
}

function gameStart() {
	socket.removeEventListener("message", waitRoom);
	socket.addEventListener("message", update);
	game_status = PLAYING;
	changeButton();
	resizeCanvas();
	canvas.focus();
}

function gameOver(is_winner) {
	game_status = LOST;
	if (is_winner)
		game_status = WON;
	socket.close();
	resizeCanvas();
}

function gameTick() {
	updateFrame();
}

function submitInput(dir, action) {
	socket.send(new Uint8Array([false, dir, action]));
}

function GiveUp() {
	socket.send(new Uint8Array([true, false, false]));
}

function update(event) {
	var received_data = JSON.parse(event.data);
	if (received_data.type == "tick") {
		to_add.push(received_data.tiles);
		gameTick();
		return ;
	}
	console.log(received_data);				// DEBUG
	if (received_data.type == "start") {
		grid.size = received_data.grid;
		grid = Array(grid_size[0]);
		grid.fill(Uint8Array(grid_size[1]));
		resizeCanvas();
		colors = received_data.colors;
		for (snake of received_data.snakes) {
			for (segment of snake) {
				to_add.push([x[0], x[1], received_data.color]);
			}
		}
		return ;
	}
	if (received_data.type == "win") {
		gameOver(received_data.player);
		return ;
	}
}

function clearCanvas() {
	ctx.fillStyle = colors[0];
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	// border
	ctx.lineJoin = "bevel";
	ctx.lineWidth = block_size;
	ctx.strokeStyle = 0xffffff;
	ctx.strokeRect(margins[0] - block_size / 2, margins[1] - block_size / 2, block_size * (grid_size[0] - 1), block_size * (grid_size[1] - 1));
}

function drawFrame() {
	clearCanvas();
	// fill tiles
	for (x in grid) {
		for (y in grid[x])
			if (grid[x][y])
				drawTile([x, y], grid[x][y]);
	}
}

function updateFrame() {
	while (to_add.length) {
		let tile = to_add.shift();
		grid[tile[0]][tile[1]] = tile[2];
		drawTile(tile, tile[2]);
	}
}

function drawTile(coords, value) {
	ctx.fillStyle = colors[value];
	ctx.fillRect(margins[0] + block_size * coords[0], margins[1] + block_size * coords[1], block_size, block_size);
}

function drawMessage(message) {
	clearCanvas();
	ctx.fillStyle = "white";
	// message
	ctx.font = canvas.height / 20 + "px arial";
	ctx.textBaseline = "middle";
	ctx.textAlign = "center";
	ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}
