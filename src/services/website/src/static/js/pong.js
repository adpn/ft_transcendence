const UP = true;
const DOWN = false;
const START = true;
const STOP = false;
const LEFT = false;
const RIGHT = true;

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
var ctx = null;
var is_focus = false;
var game_status = NOT_JOINED;
var bytes_array = new Uint8Array(4);


// function disconnected() {
// 	if (game_status <= PLAYING)
// 		game_status = DISCONNECTED;
// 	resizeCanvas();
// 	changeButton();
// }

function changeButton() {
	switch (game_status) {
		// case NOT_JOINED:
		// case WON:
		// case LOST:
		// case DISCONNECTED:
		// 	var title = "find game";
		// 	var btn_class = "success";
		// 	break ;
		// case CONNECTING:
		// 	var title = "cancel";
		// 	var btn_class = "danger";
		// 	break ;
		case PLAYING:
			var title = "give up";
			var btn_class = "warning";
	}
// 	document.getElementById("game-button-container").innerHTML = `
// 		<button class="btn btn-${btn_class} me-2" id="game-button" type="button">${title}</button>
// `;
	// var button = document.getElementById("game-button");
	// switch (game_status) {
	// 	// case NOT_JOINED:
	// 	// case WON:
	// 	// case LOST:
	// 	// case DISCONNECTED:
	// 	// 	button.addEventListener("click", connectGameRoom);
	// 	// 	break ;
	// 	// case CONNECTING:
	// 	// 	// todo: put a spinning animation
	// 	// 	button.addEventListener("click", cancel);
	// 	// 	break ;
	// 	case PLAYING:
	// 		button.addEventListener("click", GiveUp);
	// }
}

function takeInputDown(e) {
	if (!is_focus || e.defaultPrevented) {
		return ;
	}
	switch (e.key) {
		case "w":
			submitInput(UP, START, LEFT);
			break ;
		case "ArrowUp":
			submitInput(UP, START, RIGHT);
			break ;
		case "s":
			submitInput(DOWN, START, LEFT);
			break ;
		case "ArrowDown":
			submitInput(DOWN, START, RIGHT);
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
			submitInput(UP, STOP, LEFT);
			break ;
		case "ArrowUp":
			submitInput(UP, STOP, RIGHT);
			break ;
		case "s":
			submitInput(DOWN, STOP, LEFT);
			break ;
		case "ArrowDown":
			submitInput(DOWN, STOP, RIGHT);
			break ;
	}
	e.preventDefault();
}

function resizeCanvas() {
	canvas.width = canvas.scrollWidth;
	canvas.height = canvas.scrollHeight;
	clearCanvas(canvas, ctx);
	switch (game_status) {
	// 	case NOT_JOINED:
	// 		drawMessage("Welcome", canvas, ctx);
	// 		break ;
	// 	case CONNECTING:
	// 		drawMessage("Connecting...", canvas, ctx);
	// 		break ;
	case PLAYING:
		drawFrame(canvas, ctx, game_data);
		break ;
	// 	case WON:
	// 		drawMessage("Victory", canvas, ctx);
	// 		drawScore(canvas, game_data);
	// 		break ;
	// 	case LOST:
	// 		drawMessage("Defeat", canvas, ctx);
	// 		drawScore(canvas, game_data);
	// 		break ;
	// 	case DISCONNECTED:
	// 		drawMessage("Disconnected", canvas, ctx);
	// 		break ;
	// 	case NOT_LOGGED:
	// 		drawMessage("You are not logged in", canvas, ctx);
	// 		break ;
	// 	case ERROR:
	// 		drawMessage("Something went wrong", canvas, ctx);
	}
}

function makeXCord(number, canvas) {
	return number * (canvas.width / 1000);
}
function makeYCord(number, canvas) {
	return number * (canvas.height / 1000);
}

// function gameStart(sockt) {
// 	socket = sockt;
// 	sockt.addEventListener("message", updatePong);
// 	game_status = PLAYING;
// 	changeButton();
// 	resizeCanvas();
// 	canvas.focus();
// }

function gameOver(gameStatus) {
	if (gameStatus == 'win')
		game_status = WON
	else
		game_status = LOST
	socket.close();
	resizeCanvas();
}

function gameTick(canvas, ctx, game_data) {
	clearCanvas(canvas, ctx);
	drawFrame(canvas, ctx, game_data);
}

function submitInput(dir, action, position) {
	bytes_array[0] = false;
	bytes_array[1] = dir;
	bytes_array[2] = action;
	bytes_array[3] = position;
	socket.send(bytes_array);
}

function clearCanvas(canvas, ctx) {
	ctx.fillStyle = "black";
	ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawFrame(canvas, ctx, game_data) {
	ctx.fillStyle = "white";
	// centerline
	ctx.fillRect(canvas.width / 2 - makeXCord(1, canvas), 0, makeXCord(2, canvas), canvas.height);
	// ball
	ctx.fillRect(makeXCord(game_data.ball_pos[0], canvas) - makeXCord(game_data.ball_size / 2, canvas), makeYCord(game_data.ball_pos[1], canvas) - makeYCord(game_data.ball_size / 2, canvas),
			makeXCord(game_data.ball_size, canvas), makeXCord(game_data.ball_size, canvas));
	// rackets
	ctx.fillRect(makeXCord(5, canvas), makeYCord(game_data.racket_pos[0], canvas), makeXCord(10, canvas), makeYCord(game_data.racket_size[0], canvas));
	ctx.fillRect(canvas.width - makeXCord(15, canvas), makeYCord(game_data.racket_pos[1], canvas), makeXCord(10, canvas), makeYCord(game_data.racket_size[1], canvas));
	drawScore(canvas, ctx, game_data);
}

function drawMessage(message, canvas, ctx, game_data) {
	ctx.fillStyle = "white";
	// rackets
	ctx.fillRect(makeXCord(5, canvas), makeYCord(game_data.racket_pos[0]), makeXCord(10, canvas), makeYCord(game_data.racket_size[0], canvas));
	ctx.fillRect(canvas.width - makeXCord(15, canvas), makeYCord(game_data.racket_pos[1], canvas), makeXCord(10, canvas), makeYCord(game_data.racket_size[1], canvas));
	// message
	ctx.font = makeXCord(40, canvas) + "px arial";
	ctx.textBaseline = "middle";
	ctx.textAlign = "center";
	ctx.fillText(message, makeXCord(500, canvas), makeYCord(500, canvas));
}

function drawScore(canvas, ctx, game_data) {
	ctx.font = makeXCord(30, canvas) + "px arial";
	ctx.textBaseline = "top";
	ctx.textAlign = "center";
	ctx.fillText(game_data.score[0], makeXCord(480, canvas), makeYCord(15, canvas));
	ctx.fillText(game_data.score[1], makeXCord(520, canvas), makeYCord(15, canvas));
}

export var Pong = {
	name: "pong",
	canvas_context: "2D",
	load(canv) {
		canvas = canv;
		canvas.setAttribute("tabindex", "-1");
		canvas.addEventListener("focus", () => { is_focus = true; });
		canvas.addEventListener("blur", () => { is_focus = false; });
		if (!ctx) {
			ctx = canvas.getContext("2d", { alpha: false });
			if (!ctx) {
				console.log("ERROR: pong.js: Couldn't create 2D drawing context");
				return ;
			}
		}
		window.addEventListener("resize", resizeCanvas, false);
		game_status = PLAYING;
		changeButton();
		resizeCanvas();
		canvas.focus();
	},
	start(sockt) {
		socket = sockt;
		game_status = PLAYING;
		changeButton();
		resizeCanvas();
		canvas.focus();
		window.addEventListener("keydown", takeInputDown, true);
		window.addEventListener("keyup", takeInputUp, true);
	},
	clear() {
		window.removeEventListener("keydown", takeInputDown, true);
		window.removeEventListener("keyup", takeInputUp, true);
		window.removeEventListener("resize", resizeCanvas, false);
		ctx = null;
	},
	update(data) {
		if (game_status != PLAYING)
			return ;
		if (data.type == "tick") {
			game_data.ball_pos = data.b;
			game_data.racket_pos = data.r;
			gameTick(canvas, ctx, game_data);
			return ;
		}
		if (data.type == "goal") {
			game_data.score = data.score;
			return ;
		}
		if (data.type == "start") {
			game_data.ball_size = data.ball_size;
			game_data.racket_size = data.racket_size;
			game_data.score = data.score;
			return ;
		}
		if (data.type == "end") {		// this is never called i think, the gameModesStates don't pass it along
			gameOver(data.status);
			return ;
		}
	},
	giveUp(socket) {
		bytes_array[0] = true;
		socket.send(bytes_array);
	}
};
