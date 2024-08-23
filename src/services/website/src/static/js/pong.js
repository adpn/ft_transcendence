// import * as THREE from 'three';

const UP = true;
const DOWN = false;
const START = true;
const STOP = false;

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_pos: [500, 500],
	ball_size: 10,
	racket_pos: [400, 400],
	racket_size: [200, 200],
	score: [0, 0]
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

document.addEventListener("DOMContentLoaded", function () {
	window.addEventListener("https://localhost/pong", loadPong);
});

function loadPong() {
	window.removeEventListener("https://localhost/pong", loadPong);	// ???
	const canvas = document.getElementById("gameCanvas");
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", connectGameRoom);
	canvas.addEventListener("focus", function () { is_focus = true; });
	canvas.addEventListener("blur", function () { is_focus = false; });
	const ctx = canvas.getContext("2d");
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);
	resizeCanvas();

	function connectGameRoom() {
		canvas.removeEventListener("focus", connectGameRoom);
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
			socket = new WebSocket("ws://localhost:8001/ws/game/pong/" + data.game_room_id); // ws for now to do testing, wss later.
			if (socket.readyState > socket.OPEN)
				throw new Error("WebSocket error: " + socket.readyState);
			socket.addEventListener("close", disconnected);
			socket.addEventListener("open", function () {
				game_status = 1;
				resizeCanvas();
				// window.addEventListener("pageSwitch", function () {
				// 	socket.close();
				// 	game_status = 0;
				// });
				socket.addEventListener("message", waitRoom);
			});
		})
		.catch((error) => { console.log(error); });
	}

	function disconnected() {
		game_status = 6;
		resizeCanvas();
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
		switch (game_status) {
			case 0:
				drawMessage("Click here to find a game");
				break ;
			case 1:
				drawMessage("Connecting...");
				break ;
			case 2:
				drawFrame();
				break ;
			case 3:
				drawMessage("!! you won !!");
			case 4:
				drawMessage(".. you lost ..");
			case 6:
				drawMessage("Disconnected");
				break ;
		}
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

	function gameOver(is_winner) {
		socket.removeEventListener("close", disconnected);
		game_status = 4;
		if (is_winner)
			game_status = 3;
		socket.close();
		resizeCanvas();
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
		console.log(received_data);	// TESTING
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
		// midline
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
		ctx.font = makeXCord(30) + "px arial";
		ctx.textBaseline = "middle";
		ctx.textAlign = "center";
		ctx.fillText(message, makeXCord(500), makeYCord(500));
	}
}
