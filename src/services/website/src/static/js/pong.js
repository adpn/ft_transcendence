// import * as THREE from 'three';

const UP = true;
const DOWN = false;
const START = true;
const STOP = false;

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_posx: 500,
	ball_posy: 500,
	ball_size: 10,
	racket_left_pos: 400,
	racket_left_size: 200,
	racket_right_pos: 400,
	racket_right_size: 200,
	score_left: 0,
	score_right: 0
};

// var game_input = {
// 	left_up: false,
// 	left_down: false,
// 	right_up: false,
// 	right_down: false
// }

var socket;
var is_focus = false;
var game_status = 0;

document.addEventListener("DOMContentLoaded", function() {
	const canvas = document.getElementById("gameCanvas");
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", function () { is_focus = true; });
	canvas.addEventListener("blur", function () { is_focus = false; });
	const ctx = canvas.getContext("2d");
	window.addEventListener("load", resizeCanvas, false);
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);

	const button = document.getElementById("test-game");
	button.addEventListener("click", connectGameRoom);
	function connectGameRoom() {
		fetch("/games/create_game", {
			method: "GET",
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			},
			credentials: "include"
		})
		.then((response) => {
			if(!response.ok)
				throw new Error(response.status);
			return response.json();
		  })
        .then(data => {
			socket = new WebSocket("ws://localhost:8001/ws/game/pong/" + data.game_room_id); // ws for now to do testing, wss later.
			if (socket.readyState > socket.OPEN)
				throw new Error("WebSocket error: " + socket.readyState);
			socket.addEventListener("close", function () {
				game_status = 6;
				resizeCanvas();
				throw new Error("Websocket closed: " + socket.readyState);		// this error goes uncaught
			});
			socket.addEventListener("open", function () {
				game_status = 1;
				resizeCanvas();
				socket.addEventListener("message", waitRoom);
			});
		})
		.catch((error) => { console.log(error); });
	}

	function waitRoom(event) {
		if (JSON.parse(event.data).status != "ready")
			return ;
		socket.removeEventListener("message", waitRoom);
		socket.addEventListener("message", update);
		gameStart();
	}

	// would need to differentiate between local and network-play for input
	function takeInputDown(e) {
		if (!is_focus || e.defaultPrevented) {
			return ;
		}
		switch (e.key) {
			case "w":
			case "ArrowUp":
				submit(UP, START);
				break ;
			case "s":
			case "ArrowDown":
				submit(DOWN, START);
				break ;
		}
		e.preventDefault();
	}

	// would need to differentiate between local and network-play for input
	function takeInputUp(e) {
		if (!is_focus || e.defaultPrevented) {
			return ;
		}
		switch (e.key) {
			case "w":
			case "ArrowUp":
				submit(UP, STOP);
				break ;
			case "s":
			case "ArrowDown":
				submit(DOWN, STOP);
				break ;
		}
		e.preventDefault();
	}

	function resizeCanvas() {
		canvas.width = canvas.scrollWidth;
		canvas.height = canvas.scrollHeight;
		clearCanvas();
		if (game_status == 0)
			drawMessage("Welcome!");
		else if (game_status == 1)
			drawMessage("Connecting...");
		else if (game_status == 6)
			drawMessage("Disconnected");
		else
			drawFrame();
	}

	function makeXCord(number) {
		return number * (canvas.width / 1000);
	}
	function makeYCord(number) {
		return number * (canvas.height / 1000);
	}

	function gameStart() {
		game_status = 2;
		resizeCanvas();
		// setInterval(gameTick, 20);
	}

	function gameTick() {
		clearCanvas();
		drawFrame();
	}

	function submit(dir, action) {
		socket.send(new Uint8Array([dir, action]));
	}

	function update(event) {
		received_data = JSON.parse(event.data);
		// if (Object.keys(received_data).length == 9)
			game_data = received_data;
		gameTick();
	}

	function clearCanvas() {
		ctx.fillStyle = "black";
		ctx.fillRect(0, 0, canvas.width, canvas.height);
	}

	function drawFrame() {
		ctx.fillStyle = "white";
		// midline
		ctx.fillRect(canvas.width / 2 - makeXCord(1), 0, makeXCord(2), canvas.height);
		// ball
		ctx.fillRect(makeXCord(game_data.ball_posx) - makeXCord(game_data.ball_size / 2), makeYCord(game_data.ball_posy) - makeYCord(game_data.ball_size / 2),
				makeXCord(game_data.ball_size), makeXCord(game_data.ball_size));
		// rackets
		ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_left_pos), makeXCord(10), makeYCord(game_data.racket_left_size));
		ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_right_pos), makeXCord(10), makeYCord(game_data.racket_right_size));
		// scoreboard
		ctx.font = makeXCord(30) + "px arial";
		ctx.textBaseline = "top";
		ctx.textAlign = "center";
		ctx.fillText(game_data.score_left, makeXCord(480), makeYCord(15));
		ctx.fillText(game_data.score_right, makeXCord(520), makeYCord(15));
	}

	function drawMessage(message) {
		ctx.fillStyle = "white";
		// rackets
		ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_left_pos), makeXCord(10), makeYCord(game_data.racket_left_size));
		ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_right_pos), makeXCord(10), makeYCord(game_data.racket_right_size));
		// message
		ctx.font = makeXCord(30) + "px arial";
		ctx.textBaseline = "middle";
		ctx.textAlign = "center";
		ctx.fillText(message, makeXCord(500), makeYCord(500));
	}
});
