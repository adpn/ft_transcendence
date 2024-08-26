// import * as THREE from 'three';

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

const BTN_ID = "game-button"

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_pos: [500, 500],
	ball_size: 10,
	racket_pos: [400, 400],
	racket_size: [200, 200],
	score: [0, 0]
};

var socket;
var button;
var canvas;
var ctx;
var is_focus = false;
var game_status = NOT_JOINED;


document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("pong", loadPong);
});

function loadPong() {
	canvas = document.getElementById("gameCanvas");
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", function () { is_focus = true; });
	canvas.addEventListener("blur", function () { is_focus = false; });
	button = document.getElementById(BTN_ID);
	ctx = canvas.getContext("2d");
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
				"game": "pong"
			})
	})
	.then((response) => {
		if(!response.ok)
			throw new Error(response.status);
		return response.json();
		})
	.then(data => {
		socket = new WebSocket("wss://" + data.ip_address + "/ws/game/pong/" + data.game_room_id + "/?csrf_token=" + getCookie("csrftoken") + "&token=" + localStorage.getItem("auth_token"));
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
	.catch((error) => { console.log(error); });
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
	button.removeEventListener("click", connectGameRoom);
	button.removeEventListener("click", cancel);
	button.removeEventListener("click", GiveUp);
	switch (game_status) {
		case NOT_JOINED:
		case WON:
		case LOST:
		case DISCONNECTED:
			button.addEventListener("click", connectGameRoom);
			title = "find game";
			btn_class = "btn-success";
			break ;
		case CONNECTING:
			button.addEventListener("click", cancel);
			title = "cancel";
			btn_class = "btn-danger";
			break ;
		case PLAYING:
			button.addEventListener("click", GiveUp);
			title = "give up";
			btn_class = "btn-warning";
	}
	button.innerHTML = `
		<div id="${BTN_ID}">
			<button class="btn ${btn_class} me-2" type="button">${title}</button>
		</div>
`;
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
			break ;
		case LOST:
			drawMessage("Defeat");
			break ;
		case DISCONNECTED:
			drawMessage("Disconnected");
	}
}

function makeXCord(number) {
	return number * (canvas.width / 1000);
}
function makeYCord(number) {
	return number * (canvas.height / 1000);
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
	clearCanvas();
	drawFrame();
}

function submitInput(dir, action) {
	socket.send(new Uint8Array([false, dir, action]));
}

function GiveUp() {
	socket.send(new Uint8Array([true, false, false]));
}

function update(event) {
	received_data = JSON.parse(event.data);
	if (received_data.type == "tick") {
		game_data.ball_pos = received_data.ball_pos;
		game_data.racket_pos = received_data.racket_pos;
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
	if (received_data.type == "win") {
		gameOver(received_data.player);
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
	// scoreboard
	ctx.font = makeXCord(30) + "px arial";
	ctx.textBaseline = "top";
	ctx.textAlign = "center";
	ctx.fillText(game_data.score[0], makeXCord(480), makeYCord(15));
	ctx.fillText(game_data.score[1], makeXCord(520), makeYCord(15));
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
