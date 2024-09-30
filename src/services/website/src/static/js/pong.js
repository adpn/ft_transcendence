const UP = true;
const DOWN = false;
const START = true;
const STOP = false;
const LEFT = false;
const RIGHT = true;

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_pos: [500, 500],
	ball_size: 10,
	racket_pos: [425, 425],
	racket_size: [150, 150],
	score: [0, 0]
};

var is_playing = false;
var socket;
var canvas;
var ctx = null;
var is_focus = false;
var bytes_array = new Uint8Array(4);

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
	drawFrame(canvas, ctx, game_data);
}

function makeXCord(number, canvas) {
	return number * (canvas.width / 1000);
}
function makeYCord(number, canvas) {
	return number * (canvas.height / 1000);
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
		is_playing = true;
		resizeCanvas();
		canvas.focus();
	},
	start(sockt) {
		socket = sockt;
		is_playing = true;
		resizeCanvas();
		canvas.focus();
		window.addEventListener("keydown", takeInputDown, true);
		window.addEventListener("keyup", takeInputUp, true);
	},
	clear() {
		is_playing = false;
		window.removeEventListener("keydown", takeInputDown, true);
		window.removeEventListener("keyup", takeInputUp, true);
		window.removeEventListener("resize", resizeCanvas, false);
		ctx = null;
	},
	update(data) {
		if (is_playing != true)
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
	},
	giveUp(socket) {
		bytes_array[0] = true;
		socket.send(bytes_array);
	}
};
