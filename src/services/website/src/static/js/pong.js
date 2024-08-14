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
	score_left: 1,
	score_right: 0
}

var game_input = {
	left_up: false,
	left_down: false,
	right_up: false,
	right_down: false
}


document.addEventListener("DOMContentLoaded", function() {
	const canvas = document.getElementById("gameCanvas");
	const ctx = canvas.getContext("2d");
	window.addEventListener("load", gameStart, false);
	window.addEventListener("resize", resizeCanvas, false);
	window.addEventListener("keydown", takeInputDown, true);
	window.addEventListener("keyup", takeInputUp, true);

	// would need to differentiate between local and network-play for input
	function takeInputDown(e) {
		if (e.defaultPrevented) {
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
		if (e.defaultPrevented) {
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
		drawFrame();
	}

	function makeXCord(number) {
		return number * (canvas.width / 1000);
	}
	function makeYCord(number) {
		return number * (canvas.height / 1000);
	}

	function gameStart() {
		resizeCanvas();
		setInterval(gameTick, 20);
	}

	function gameTick() {
		update();
		clearCanvas();
		drawFrame();
	}

	function update() {
		// replace this function with communication with the server
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
		ctx.fillText(game_data.score_left, makeXCord(480), makeXCord(10));
		ctx.fillText(game_data.score_right, makeXCord(520), makeXCord(10));
	}
});
