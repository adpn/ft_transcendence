// import * as THREE from 'three';

// this stuff is relative to a canvas of 1000,1000
var game_data = {
	ball_pos: [500,500],
	ball_size: 10,
	racket_left_pos: 400,
	racket_left_size: 200,
	racket_right_pos: 400,
	racket_right_size: 200
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
		process_input();
		clearCanvas();
		drawFrame();
	}

	function process_input() {
		// replace this function with communication with the server
		if (game_input.right_up) {
			game_data.racket_right_pos -= 10;
			if (game_data.racket_right_pos < 0)
				game_data.racket_right_pos = 0;
		}
		if (game_input.right_down) {
			game_data.racket_right_pos += 10;
			if (game_data.racket_right_pos + game_data.racket_right_size > 1000)
				game_data.racket_right_pos = 1000 - game_data.racket_right_size;
		}
		if (game_input.left_up) {
			game_data.racket_left_pos -= 10;
			if (game_data.racket_left_pos < 0)
				game_data.racket_left_pos = 0;
		}
		if (game_input.left_down) {
			game_data.racket_left_pos += 10;
			if (game_data.racket_left_pos + game_data.racket_left_size > 1000)
				game_data.racket_left_pos = 1000 - game_data.racket_left_size;
		}
	}

	function clearCanvas() {
		ctx.fillStyle = "black";
		ctx.fillRect(0, 0, canvas.width, canvas.height);
		ctx.fillStyle = "white";
		ctx.fillRect(canvas.width / 2 - makeXCord(1), 0, makeXCord(2), canvas.height);
	}

	function drawFrame() {
		ctx.fillStyle = "white";
		ctx.fillRect(makeXCord(game_data.ball_pos[0]) - makeXCord(game_data.ball_size / 2), makeYCord(game_data.ball_pos[1]) - makeYCord(game_data.ball_size / 2),
				makeXCord(game_data.ball_size), makeXCord(game_data.ball_size));
		ctx.fillRect(makeXCord(5), makeYCord(game_data.racket_left_pos), makeXCord(10), makeYCord(game_data.racket_left_size));
		ctx.fillRect(canvas.width - makeXCord(15), makeYCord(game_data.racket_right_pos), makeXCord(10), makeYCord(game_data.racket_right_size));
	}
});
