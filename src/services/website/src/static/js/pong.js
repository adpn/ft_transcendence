const UP = true;
const DOWN = false;
const START = true;
const STOP = false;

const NOT_JOINED = 0;
const CONNECTING = 1;
const PLAYING = 2;
const WON = 3;
const LOST = 4;
const DISCONNECTED = 6;
const ERROR = 7;
const NOT_LOGGED = 8;

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_pos: [500, 500],
	ball_size: 10,
	racket_pos: [425, 425],
	racket_size: [150, 150],
	score: [0, 0]
};

var socket;
var canvas;
var ctx;
var is_focus = false;
var game_status = NOT_JOINED;
var canvas_loaded = false;


function loadPong(canv) {
	canvas = canv
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", () => { is_focus = true; });
	canvas.addEventListener("blur", () => { is_focus = false; });
	ctx = canvas.getContext("2d", { alpha: false });
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);
	if (game_status >= WON)
		game_status = NOT_JOINED;
	changeButton();
	resizeCanvas();
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
		// case NOT_JOINED:
		// case WON:
		// case LOST:
		// case DISCONNECTED:
		// 	button.addEventListener("click", connectGameRoom);
		// 	break ;
		case CONNECTING:
			// todo: put a spinning animation
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
	switch (e.key) {
		case "w":
		case "ArrowUp":
			submitInput(UP, START);
			break ;
		case "s":
		case "ArrowDown":
			submitInput(DOWN, START);
			break ;
	}
	e.preventDefault();
}

function takeInputUp(e) {
	if (!is_focus || e.defaultPrevented) {
		return ;
	}
	switch (e.key) {
		case "w":
		case "ArrowUp":
			submitInput(UP, STOP);
			break ;
		case "s":
		case "ArrowDown":
			submitInput(DOWN, STOP);
			break ;
	}
	e.preventDefault();
}

function resizeCanvas() {
	canvas.width = canvas.scrollWidth;
	canvas.height = canvas.scrollHeight;
	clearCanvas();
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
			drawScore();
			break ;
		case LOST:
			drawMessage("Defeat");
			drawScore();
			break ;
		case DISCONNECTED:
			drawMessage("Disconnected");
			break ;
		case NOT_LOGGED:
			drawMessage("You are not logged in");
			break ;
		case ERROR:
			drawMessage("Something went wrong");
	}
}

function makeXCord(number) {
	return number * (canvas.width / 1000);
}
function makeYCord(number) {
	return number * (canvas.height / 1000);
}

function gameStart(sockt) {
	socket = sockt;
	sockt.addEventListener("message", updatePong);
	game_status = PLAYING;
	changeButton();
	resizeCanvas();
	canvas.focus();
}

function gameOver(gameStatus) {
	if (gameStatus == 'win')
		game_status = WON
	else
		game_status = LOST
	socket.close();
	resizeCanvas();
}

function gameTick() {
	clearCanvas();
	drawFrame();
}

function submitInput(dir, action) {
	socket.send(new Uint8Array([false, dir, action]));
}

function GiveUp() {
	socket.send(new Uint8Array([true, false, false]));
}

function updatePong(event) {
	var received_data = JSON.parse(event.data);
	if (received_data.type == "tick") {
		game_data.ball_pos = received_data.b;
		game_data.racket_pos = received_data.r;
		gameTick();
		return ;
	}
	if (received_data.type == "goal") {
		game_data.score = received_data.score;
		return ;
	}
	if (received_data.type == "start") {
		game_data.ball_size = received_data.ball_size;
		game_data.racket_size = received_data.racket_size;
		game_data.score = received_data.score;
		return ;
	}
	if (received_data.type == "end") {
		gameOver(received_data.status);
		return ;
	}
}

function clearCanvas() {
	ctx.fillStyle = "black";
	ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawFrame() {
	ctx.fillStyle = "white";
	// centerline
	ctx.fillRect(canvas.width / 2 - makeXCord(1), 0, makeXCord(2), canvas.height);
	// ball
	ctx.fillRect(makeXCord(game_data.ball_pos[0]) - makeXCord(game_data.ball_size / 2), makeYCord(game_data.ball_pos[1]) - makeYCord(game_data.ball_size / 2),
			makeXCord(game_data.ball_size), makeXCord(game_data.ball_size));
	// rackets
	ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_pos[0]), makeXCord(10), makeYCord(game_data.racket_size[0]));
	ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_pos[1]), makeXCord(10), makeYCord(game_data.racket_size[1]));
	drawScore();
}

function drawMessage(message) {
	ctx.fillStyle = "white";
	// rackets
	ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_pos[0]), makeXCord(10), makeYCord(game_data.racket_size[0]));
	ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_pos[1]), makeXCord(10), makeYCord(game_data.racket_size[1]));
	// message
	ctx.font = makeXCord(40) + "px arial";
	ctx.textBaseline = "middle";
	ctx.textAlign = "center";
	ctx.fillText(message, makeXCord(500), makeYCord(500));
}

function drawScore() {
	ctx.font = makeXCord(30) + "px arial";
	ctx.textBaseline = "top";
	ctx.textAlign = "center";
	ctx.fillText(game_data.score[0], makeXCord(480), makeYCord(15));
	ctx.fillText(game_data.score[1], makeXCord(520), makeYCord(15));
}
// });
