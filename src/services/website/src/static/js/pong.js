// import * as THREE from 'three';

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
}

var game_input = {
	left_up: false,
	left_down: false,
	right_up: false,
	right_down: false
}

var is_focus = false
var is_gaming = false

document.addEventListener("DOMContentLoaded", function() {
	const canvas = document.getElementById("gameCanvas");
	canvas.setAttribute("tabindex", "-1");
	canvas.addEventListener("focus", function () { is_focus = true; })
	canvas.addEventListener("blur", function () { is_focus = false; })
	const ctx = canvas.getContext("2d");
	window.addEventListener("load", resizeCanvas, false);
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);

	window.addEventListener("load", connectGameRoom);
	function connectGameRoom() {
		fetch("/games/create_game", {
			method: "GET",
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			},
			credentials: "include"
		})
		.then(response => response.json())
        .then(data => {
			const socket = new WebSocket("ws://localhost:8001/ws/game/pong/" + data.game_room_id); // ws for now to do testing, wss later.
			socket.addEventListener("open", gameStart);
			socket.addEventListener("message", update);
		})
	}

	// would need to differentiate between local and network-play for input
	function takeInputDown(e) {
		if (!is_focus || e.defaultPrevented) {
			return ;
		}
		switch (e.key) {
			case "ArrowUp":
				game_input.right_up = true;
				break ;
			case "ArrowDown":
				game_input.right_down = true;
				break ;
			case "w":
				game_input.left_up = true;
				break ;
			case "s":
				game_input.left_down = true;
				break ;
			default:
				return ;
		}
		e.preventDefault();
	}

	// would need to differentiate between local and network-play for input
	function takeInputUp(e) {
		if (!is_focus || e.defaultPrevented) {
			return ;
		}
		switch (e.key) {
			case "ArrowUp":
				game_input.right_up = false;
				break ;
			case "ArrowDown":
				game_input.right_down = false;
				break ;
			case "w":
				game_input.left_up = false;
				break ;
			case "s":
				game_input.left_down = false;
				break ;
			default:
				return ;
		}
		e.preventDefault();
	}

	function resizeCanvas() {
		canvas.width = canvas.scrollWidth;
		canvas.height = canvas.scrollHeight;
		clearCanvas();
		if (is_gaming)
			drawFrame();
		else
			drawConnecting();
	}

	function makeXCord(number) {
		return number * (canvas.width / 1000);
	}
	function makeYCord(number) {
		return number * (canvas.height / 1000);
	}

	function gameStart() {
		is_gaming = true;
		resizeCanvas();
		setInterval(gameTick, 20);
	}

	function gameTick() {
		submit();
		clearCanvas();
		drawFrame();
	}

	function submit() {
		socket.send(game_input);
	}

	function update(event) {
		received_data = JSON.parse(event.data);
		console.log(received_data);								// TESTING
		game_data.ball_posx = received_data["ball_posx"];
		game_data.ball_posy = received_data["ball_posy"];
		game_data.ball_size = received_data["ball_size"];
		game_data.racket_left_pos = received_data["racket_left_pos"];
		game_data.racket_left_size = received_data["racket_left_size"];
		game_data.racket_right_pos = received_data["racket_right_pos"];
		game_data.racket_right_size = received_data["racket_right_size"];
		game_data.score_left = received_data["score_left"];
		game_data.score_right = received_data["score_right"];
	}

	function clearCanvas() {
		ctx.fillStyle = "black";
		ctx.fillRect(0, 0, canvas.width, canvas.height);
		ctx.fillStyle = "white";
		ctx.fillRect(canvas.width / 2 - makeXCord(1), 0, makeXCord(2), canvas.height);
	}

	function drawFrame() {
		ctx.fillStyle = "white";
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

	function drawConnecting() {
		ctx.fillStyle = "white";
		// rackets
		ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_left_pos), makeXCord(10), makeYCord(game_data.racket_left_size));
		ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_right_pos), makeXCord(10), makeYCord(game_data.racket_right_size));
		// message
		ctx.font = makeXCord(30) + "px arial";
		ctx.textBaseline = "middle";
		ctx.textAlign = "center";
		ctx.fillText("connecting...", makeXCord(500), makeYCord(500));
	}
});
