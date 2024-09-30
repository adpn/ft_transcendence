const KEY_DOWN = true;
const DIR_UP = 0;
const DIR_DOWN = 3;
const DIR_LEFT = 1;
const DIR_RIGHT = 2;
const SIDE_LEFT = false;
const SIDE_RIGHT = true;

var grid_size = [20, 20];
var block_size = 50;
var margins = [300, 100];
var grid;
var colors = [0x000000];
var ui_colors = [1, 2];
var current_ui = 0;
var to_add = [];
var snake_length = [0, 0];
var border_width;

var socket;
var canvas;
var ctx = null;
var is_focus = false;
var is_playing = false;
var bytes_array = new Uint8Array(4);

function takeInputDown(e) {
	if (!is_focus || e.defaultPrevented) {
		return ;
	}
	let dir = extractDir(e.key);
	if (dir == -1)
		return ;
	submitInput(dir, KEY_DOWN, extractSide(e.key));
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
		default :
			return -1;
	}
}

function extractSide(key) {
	switch (key) {
		case "w":
		case "a":
		case "s":
		case "d":
			return SIDE_LEFT;
		case "ArrowUp":
		case "ArrowLeft":
		case "ArrowDown":
		case "ArrowRight":
			return SIDE_RIGHT;
	}
}

function resizeCanvas() {
	canvas.width = canvas.scrollWidth;
	canvas.height = canvas.scrollHeight;
	block_size = Math.min(canvas.width / (grid_size[0] + 4), canvas.height / (grid_size[1] + 6));
	border_width = canvas.height / 100;
	margins[0] = (canvas.width - block_size * grid_size[0]) / 2;
	margins[1] = (canvas.height - block_size * grid_size[1]) / 2;
	drawFrame();
}

function gameTick() {
	updateFrame();
}

function submitInput(dir, action, side) {
	bytes_array[0] = false;
	bytes_array[1] = dir;
	bytes_array[2] = action;
	bytes_array[3] = side;
	socket.send(bytes_array);
}

function updateStart(data) {
	grid_size = data.grid;
	grid = Array(grid_size[0]);
	for (let n = 0; n < grid_size[0]; ++n)
		grid[n] = new Uint8Array(grid_size[1]);
	resizeCanvas();
	for (const value in data.colors) {
		colors[value] = data.colors[value];
	}
	snake_length = [0, 0];
	for (const player in data.snakes) {
		for (const segment of data.snakes[player]) {
			snake_length[player]++;
			to_add.push([segment[0], segment[1], data.color[player]]);
		}
	}
	ui_colors[0] = data.color[2];
	ui_colors[1] = data.color[3];
	clearCanvas();
	gameTick();
}

function clearCanvas() {
	ctx.fillStyle = colors[0];
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	drawUI();
}

function drawUI() {
	// border
	ctx.lineJoin = "bevel";
	ctx.lineWidth = border_width;
	ctx.strokeStyle = colors[ui_colors[current_ui]];
	ctx.strokeRect(margins[0] - ctx.lineWidth / 2, margins[1] - ctx.lineWidth / 2, block_size * grid_size[0] + ctx.lineWidth, block_size * grid_size[1] + ctx.lineWidth);
	updateLengthScore();
}

function updateLengthScore() {
	ctx.fillStyle = colors[0];
	let font_size = block_size * grid_size[0] / 15;
	// left clearing
	ctx.fillRect(margins[0], margins[1] - border_width - font_size * 1.2, font_size * 3, font_size);
	// right clearing
	ctx.fillRect(canvas.width - margins[0] - font_size * 3, margins[1] - border_width - font_size * 1.2, font_size * 3, font_size);
	ctx.fillStyle = colors[ui_colors[0]];
	ctx.font = font_size + "px arial";
	ctx.textBaseline = "bottom";
	ctx.textAlign = "center";
	// left drawing
	ctx.fillText(snake_length[0], margins[0] + font_size * 2, margins[1] - border_width - font_size * 0.2, font_size * 3);
	// right drawing
	ctx.fillStyle = colors[ui_colors[1]];
	ctx.fillText(snake_length[1], canvas.width - margins[0] - font_size * 2, margins[1] - border_width - font_size * 0.2, font_size * 3);
}

function drawFrame() {
	clearCanvas();
	// fill tiles
	for (const x in grid) {
		for (const y in grid[x])
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
	ctx.fillStyle = colors[0];
	ctx.fillRect((margins[0] + block_size * coords[0]) + block_size / 10, (margins[1] + block_size * coords[1]) + block_size / 10, block_size * 8 / 10, block_size * 8 / 10);
	if (value) {
		ctx.fillStyle = colors[value];
		ctx.fillRect((margins[0] + block_size * coords[0]) + block_size / 5, (margins[1] + block_size * coords[1]) + block_size / 5, block_size * 3 / 5, block_size * 3 / 5);
	}
}

export var Snake = {
	name: "snake",
	canvas_context: "2D",
	load(canv) {
		canvas = canv;
		canvas.setAttribute("tabindex", "-1");
		canvas.addEventListener("focus", () => { is_focus = true; });
		canvas.addEventListener("blur", () => { is_focus = false; });
		if (!ctx) {
			ctx = canvas.getContext("2d", { alpha: false });
			if (!ctx) {
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
		current_ui = 0;
		resizeCanvas();
		canvas.focus();
		window.addEventListener("keydown", takeInputDown, true);
	},
	clear() {
		is_playing = false;
		window.removeEventListener("keydown", takeInputDown, true);
		window.removeEventListener("resize", resizeCanvas, false);
		ctx = null;
	},
	update(data) {
		if (is_playing != true)
			return ;
		if (data.type == "tick") {
			if (data.tiles.length) {
				for (const tile of data.tiles)
					to_add.push(tile);
				gameTick();
			}
			return ;
		}
		if (data.type == "grow") {
			let updateUI = false;
			if (snake_length[0] - snake_length[1] == 0)
			{
				current_ui = 0;
				if (data.len[1] > data.len[0])
					current_ui = 1;
				updateUI = true;
			}
			snake_length = data.len;
			if (updateUI)
				drawFrame();
			else
				updateLengthScore();
			return ;
		}
		if (data.type == "start") {
			updateStart(data);
			return ;
		}
	}
};
