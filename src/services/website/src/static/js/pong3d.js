import * as THREE from 'three';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';

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

const HEIGHT = 600;
const OBJECT_HEIGHT = 10;

// this stuff is relative to a canvas of 1000,1000 (makes for a fun game >:D)
var game_data = {
	ball_pos: [500, 500],
	ball_size: 10,
	racket_pos: [425, 425],
	racket_size: [150, 150],
	score: [0, 0],
	score_old: [0, 0]
};

var socket;
var canvas;
var scene = null;
var object_ids;
function reset_ids_dict() {
	return {
		alight: -1,
		light: [-1, -1],
		floor: -1,
		line: -1,
		racket: [-1, -1],
		ball: -1,
		score: [-1, -1],
		message: -1,
		message_light: -1
	};
}
var renderer;
var animation_id;
var camera;
var font;
var is_focus = false;
var game_status = NOT_JOINED;
var bytes_array = new Uint8Array(4);


// function loadPong() {
// 	canvas = document.getElementById("gameCanvas");
// 	canvas.setAttribute("tabindex", "-1");
// 	canvas.addEventListener("focus", function () { is_focus = true; });
// 	canvas.addEventListener("blur", function () { is_focus = false; });
// 	window.addEventListener("resize", resizeCanvas, false);
// 	window.addEventListener("keydown", takeInputDown, true);
// 	window.addEventListener("keyup", takeInputUp, true);
// 	if (game_status >= WON)
// 		game_status = NOT_JOINED;
// 	changeButton();
// 	loadThreejs();
// }

function loadThreejs() {
	if (scene)
		return ;
	object_ids = reset_ids_dict();
	scene = new THREE.Scene();
	renderer = new THREE.WebGLRenderer( { canvas: canvas } );
	if (!scene || !renderer)
		return -1;
	renderer.setClearColor(0xebebf5);
	renderer.shadowMap.enabled = true;
	renderer.shadowMap.type = THREE.PCFSoftShadowMap;
	camera = new THREE.PerspectiveCamera(70, canvas.scrollWidth / canvas.scrollHeight, 1, 1000);
	camera.position.set(0, -270, 470);
	camera.rotation.x = 0.35;
	resizeCanvas();
	loadLights();
	loadFloor();
	loadGear();
	loadText();
	// tool stuff ...
	// scene.add(new THREE.AxesHelper(10));						// DEBUG
	// scene.add(new THREE.CameraHelper(light.shadow.camera));	// DEBUG
	let render = function() {
		animation_id = requestAnimationFrame(render);
		renderer.render(scene, camera);
	};
	render();
}

function loadLights() {
	// alight
	var alight = new THREE.AmbientLight(0xffffff, 0.1);
	scene.add(alight);
	object_ids.alight = alight.id;
	// pointlight
	/* var light = new THREE.PointLight(0xffffff, 50, 0, 0.5);		// (color, intensity[1], distance[0], decay[2])
	light.position.set(0, HEIGHT / 10, 100 + OBJECT_HEIGHT);	// (right, up, close)(width, length, height)
	light.castShadow = true;
	light.shadow.mapSize.width = 1024;  // Default is 512
    light.shadow.mapSize.height = 1024; // Default is 512
    light.shadow.camera.near = 70;    // Default is 0.5
    light.shadow.camera.far = 800;      // Default is 500
	scene.add(light);
	object_ids.light = light.id; */
	// spotlights
	var light = new THREE.SpotLight(0xffffff, 20, 0, Math.PI / 3, 0.2, 0.3);	// (color, intensity[1], distance[0], angle[pi/3], penumbra[0], decay[2])
	light.position.set(650, 0, 200);
	light.castShadow = true;
	light.shadow.mapSize.width = 1024;
    light.shadow.mapSize.height = 1024;
    light.shadow.camera.near = 70;
    light.shadow.camera.far = 1300;
	scene.add(light);
	object_ids.light[1] = light.id;
	// scene.add(new THREE.CameraHelper(light.shadow.camera));					// DEBUG
	light = light.clone();
	light.position.x *= -1;
	scene.add(light);
	object_ids.light[0] = light.id;
	// scene.add(new THREE.CameraHelper(light.shadow.camera));					// DEBUG
	// message_light
	light = new THREE.PointLight(0xffffff, 600, 0, 1);
	light.position.set(0, -230, 350);
	light.castShadow = true;
	light.shadow.mapSize.width = 1024;
    light.shadow.mapSize.height = 1024;
    light.shadow.camera.near = 1;
    light.shadow.camera.far = 1000;
	light.visible = false;
	scene.add(light);
	object_ids.message_light = light.id;
}

function loadFloor() {
	// floor plane
	let geometry = new THREE.PlaneGeometry(1200, HEIGHT + HEIGHT / 5);
	let material = new THREE.MeshStandardMaterial( {color: 0x1f51ff, side: THREE.FrontSide} );	// green: 0x41980a, light_blue: 0xabd1f3, dark_blue: 0x1f51ff
	var floor = new THREE.Mesh(geometry, material);
	floor.position.set(0, 0, -OBJECT_HEIGHT);
	floor.receiveShadow = true;
	scene.add(floor);
	object_ids.floor = floor.id;
	// floor lines
	geometry = new THREE.BufferGeometry();
	const border_width = 10;
	const vertices = new Float32Array([
		-500, HEIGHT / 2, -OBJECT_HEIGHT + 0.01,									// 0
		500, HEIGHT / 2, -OBJECT_HEIGHT + 0.01,										// 1
		500 + border_width, HEIGHT / 2 + border_width, -OBJECT_HEIGHT + 0.01,		// 2
		-(500 + border_width), HEIGHT / 2 + border_width, -OBJECT_HEIGHT + 0.01,	// 3
		-(500 + border_width), -(HEIGHT / 2 + border_width), -OBJECT_HEIGHT + 0.01,	// 4
		500 + border_width, -(HEIGHT / 2 + border_width), -OBJECT_HEIGHT + 0.01,	// 5
		500, -(HEIGHT / 2), -OBJECT_HEIGHT + 0.01,									// 6
		-500, -(HEIGHT / 2), -OBJECT_HEIGHT + 0.01,									// 7
		-(border_width / 2), -(HEIGHT / 2), -OBJECT_HEIGHT + 0.01,					// 8
		border_width / 2, -(HEIGHT / 2), -OBJECT_HEIGHT + 0.01,						// 9
		border_width / 2, HEIGHT / 2, -OBJECT_HEIGHT + 0.01,						// 10
		-(border_width / 2), HEIGHT / 2, -OBJECT_HEIGHT + 0.01						// 11
	]);
	const indices = [
		0, 1, 2, 2, 3, 0,	// top line
		4, 5, 6, 6, 7, 4,	// bottom line
		6, 5, 2, 2, 1, 6,	// right line
		4, 7, 0, 0, 3, 4,	// left line
		8, 9, 10, 10, 11, 8	// center line
	];
	geometry.setIndex(indices);
	geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
	geometry.computeVertexNormals();
	material = new THREE.MeshStandardMaterial( { color: 0xffffff } );
	var border = new THREE.Mesh(geometry, material);
	border.receiveShadow = true;
	scene.add(border);
	object_ids.line = border.id;
}

function loadGear() {
	// left racket
	let material = new THREE.MeshStandardMaterial({color: 0xbf8bff});				// violet: 0xbf8bff, blue: 0x4890fe
	let geometry = new THREE.BoxGeometry(10, makeYHeight(game_data.racket_size[0]), OBJECT_HEIGHT);
	var left_racket = new THREE.Mesh(geometry, material);
	left_racket.position.set(makeXCord(10), makeYCord(game_data.racket_pos[0] + game_data.racket_size[0] / 2), 0);
	left_racket.castShadow = true;
	left_racket.receiveShadow = true;
	scene.add(left_racket);
	object_ids.racket[0] = left_racket.id;
	// right racket
	geometry = new THREE.BoxGeometry(10, makeYHeight(game_data.racket_size[1]), OBJECT_HEIGHT);
	var right_racket = new THREE.Mesh(geometry, material);
	right_racket.position.set(makeXCord(990), makeYCord(game_data.racket_pos[1] + game_data.racket_size[1] / 2), 0);
	right_racket.castShadow = true;
	right_racket.receiveShadow = true;
	scene.add(right_racket);
	object_ids.racket[1] = right_racket.id;
	// ball (now in disk shape)
	geometry = new THREE.CylinderGeometry(makeYHeight(game_data.ball_size), makeYHeight(game_data.ball_size), OBJECT_HEIGHT);
	var ball = new THREE.Mesh(geometry, material);
	ball.position.set(0, 0, 0);
	ball.rotation.x += Math.PI / 2;
	ball.castShadow = true;
	ball.receiveShadow = true;
	scene.add(ball);
	object_ids.ball = ball.id;
}

function loadText() {
	// score
	let tmaterial = new THREE.MeshPhongMaterial( { color: 0xffffff, specular: 0x444444, shininess: 20 } );
	const loader = new FontLoader();
	loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', function (loaded_font) {
		font = loaded_font;
		var left_score = new THREE.Mesh(createScoreGeometry(0), tmaterial);
		left_score.position.set(-50, HEIGHT / 3.2, OBJECT_HEIGHT * 3.5);
		left_score.rotation.x += 0.4;
		left_score.castShadow = true;
		left_score.receiveShadow = true;
		scene.add(left_score);
		object_ids.score[0] = left_score.id;
		var right_score = left_score.clone();			// cloning score here, assuming both are 0 at start
		right_score.position.x *= -1;
		scene.add(right_score);
		object_ids.score[1] = right_score.id;
	});
	// message
	var message = new THREE.Mesh(undefined, tmaterial);
	message.position.set(0, -150, 250);
	// message.rotation.x += 0.4;
	message.castShadow = true;
	message.receiveShadow = true;
	message.visible = false;
	scene.add(message);
	object_ids.message = message.id;
}

function createScoreGeometry(index) {
	var score_geo = new TextGeometry(game_data.score[index].toString(), {
		font: font,
		size: 50,
		depth: 5,
		curveSegments: 10,
		bevelEnabled: true,
		bevelThickness: 1,
		bevelSize: 1,
		bevelSegments: 5
	});
	score_geo.center();
	return score_geo;
}

// function connectGameRoom() {
// 	fetch("/games/create_game/", {
// 		method: "POST",
// 		headers: {
// 			"X-CSRFToken": getCookie("csrftoken"),
// 			"Authorization": "Bearer " + localStorage.getItem("auth_token")
// 		},
// 		credentials: "include",
// 			body: JSON.stringify({
// 				"game": "pong"
// 			})
// 	})
// 	.then((response) => {
// 		if(!response.ok)
// 			throw new Error(response.status);
// 		return response.json();
// 		})
// 	.then(data => {
// 		socket = new WebSocket("wss://" + data.ip_address + "/ws/game/pong/" + data.game_room_id + "/?csrf_token=" + getCookie("csrftoken") + "&token=" + localStorage.getItem("auth_token"));
// 		if (socket.readyState > socket.OPEN)
// 			throw new Error("WebSocket error: " + socket.readyState);
// 		socket.addEventListener("close", disconnected);
// 		socket.addEventListener("open", function () {
// 			game_status = CONNECTING;
// 			updateMessage();
// 			changeButton();
// 			socket.addEventListener("message", waitRoom);
// 		});
// 	})
// 	.catch((error) => {
// 		game_status = ERROR
// 		updateMessage();
// 		console.log(error);
// 	});
// }

function cancel() {
	socket.close();
	socket = null;
}

// function disconnected() {
// 	if (game_status <= PLAYING)
// 		game_status = DISCONNECTED;
// 	updateMessage();
// 	changeButton();
// }

function waitRoom(e) {
	if (JSON.parse(e.data).status != "ready")
		return ;
	gameStart();
}

function changeButton() {
	switch (game_status) {
		// case NOT_JOINED:
		// case WON:
		// case LOST:
		// case DISCONNECTED:
		// 	var title = "find game";
		// 	var btn_class = "success";
		// 	break ;
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
	renderer.setSize(canvas.width, canvas.height, false);
	renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
	camera.aspect = canvas.width / canvas.height;
	camera.updateProjectionMatrix();
}

function updateMessage() {
	clearMessage();
	switch (game_status) {
		case NOT_JOINED:
			drawMessage("Welcome");
			break ;
		case CONNECTING:
			drawMessage("Connecting...");
			break ;
		case WON:
			drawMessage("Victory");
			break ;
		case LOST:
			drawMessage("Defeat");
			break ;
		case DISCONNECTED:
			drawMessage("Disconnected");
			break ;
		case ERROR:
			drawMessage("Server error");
	}
}

function makeXCord(number) {
	return number - 500;
}
function makeYCord(number) {
	return makeYHeight((number - 500) * -1);
}
function makeYHeight(number) {
	return number * HEIGHT / 1000;
}

// function gameStart() {
// 	socket.removeEventListener("message", waitRoom);
// 	socket.addEventListener("message", update);
// 	game_status = PLAYING;
// 	changeButton();
// 	updateMessage();
// 	canvas.focus();
// }

function gameOver(is_winner) {
	game_status = LOST;
	if (is_winner)
		game_status = WON;
	socket.close();
	socket = null;
	updateMessage();
	canvas = null;
}

function submitInput(dir, action, side) {
	bytes_array[0] = false;
	bytes_array[1] = dir;
	bytes_array[2] = action;
	bytes_array[3] = side;
	socket.send(bytes_array);
}

function GiveUp() {
	bytes_array[0] = true;
	socket.send(bytes_array);
}

// function update(event) {
// 	var received_data = JSON.parse(event.data);
// 	if (received_data.type == "tick") {
// 		game_data.ball_pos = received_data.b;
// 		game_data.racket_pos = received_data.r;
// 		updatePositions();
// 		return ;
// 	}
// 	if (received_data.type == "goal") {
// 		game_data.score = received_data.score;
// 		updateScore();
// 		return ;
// 	}
// 	if (received_data.type == "start") {
// 		game_data.ball_size = received_data.ball_size;
// 		game_data.racket_size = received_data.racket_size;
// 		game_data.score = received_data.score;
// 		updateSizes();
// 		updatePositions();
// 		updateScore();
// 		return ;
// 	}
// 	if (received_data.type == "win") {
// 		gameOver(received_data.player);
// 		return ;
// 	}
// }

function updateSizes() {
	// ball
	let object = scene.getObjectById(object_ids.ball);
	object.geometry.dispose();
	object.geometry = new THREE.CylinderGeometry(makeYHeight(game_data.ball_size), makeYHeight(game_data.ball_size), OBJECT_HEIGHT);
	// rackets
	object = scene.getObjectById(object_ids.racket[0]);
	object.geometry.dispose();
	object.geometry = new THREE.BoxGeometry(10, makeYHeight(game_data.racket_size[0]), OBJECT_HEIGHT);
	object = scene.getObjectById(object_ids.racket[1]);
	object.geometry.dispose();
	object.geometry = new THREE.BoxGeometry(10, makeYHeight(game_data.racket_size[1]), OBJECT_HEIGHT);
}

function updatePositions() {
	// ball
	let temp = scene.getObjectById(object_ids.ball);
	temp.position.set(makeXCord(game_data.ball_pos[0]), makeYCord(game_data.ball_pos[1]), 0);
	// rackets
	temp = scene.getObjectById(object_ids.racket[0]);
	temp.position.set(makeXCord(10), makeYCord(game_data.racket_pos[0] + game_data.racket_size[0] / 2), 0);
	temp = scene.getObjectById(object_ids.racket[1]);
	temp.position.set(makeXCord(990), makeYCord(game_data.racket_pos[1] + game_data.racket_size[1] / 2), 0);
}

function updateScore() {
	if (game_data.score[0] != game_data.score_old[0]) {
		let temp = scene.getObjectById(object_ids.score[0]);
		if (temp) {
			temp.geometry.dispose();
			temp.geometry = createScoreGeometry(0);
		}
	}
	if (game_data.score[1] != game_data.score_old[1]) {
		let temp = scene.getObjectById(object_ids.score[1]);
		if (temp) {
			temp.geometry.dispose();
			temp.geometry = createScoreGeometry(1);
		}
	}
	game_data.score_old = game_data.score;
}

function drawMessage(message) {
	if (object_ids.message == -1)
		return ;
	let object = scene.getObjectById(object_ids.message);
		let geo = new TextGeometry(message, {
			font: font,
			size: 50,
			depth: 5,
			curveSegments: 10,
			bevelEnabled: true,
			bevelThickness: 1,
			bevelSize: 1,
			bevelSegments: 5
		});
		geo.center();
		object.geometry = geo;
		object.visible = true;
	scene.getObjectById(object_ids.message_light).visible = true;
	scene.getObjectById(object_ids.light[0]).visible = false;
	scene.getObjectById(object_ids.light[1]).visible = false;
}

function clearMessage() {
	if (object_ids.message == -1)
		return ;
	let object = scene.getObjectById(object_ids.message);
	object.visible = false;
	if (object.geometry)
		object.geometry.dispose();
	scene.getObjectById(object_ids.message_light).visible = false;
	scene.getObjectById(object_ids.light[0]).visible = true;
	scene.getObjectById(object_ids.light[1]).visible = true;
}

export var Pong3d = {
	name: "pong",
	load(canv) {
		canvas = canv;
		canvas.setAttribute("tabindex", "-1");
		canvas.addEventListener("focus", () => { is_focus = true; });
		canvas.addEventListener("blur", () => { is_focus = false; });
		if (loadThreejs() == -1)
			throw Error("Couldn't create 3D drawing context");
		game_status = PLAYING;
		changeButton();
		window.addEventListener("resize", resizeCanvas, false);
		canvas.focus();
	},
	start(sockt) {
		socket = sockt;
		game_status = PLAYING;
		changeButton();
		canvas.focus();
		window.addEventListener("keydown", takeInputDown, true);
		window.addEventListener("keyup", takeInputUp, true);
	},
	clear() {
		window.removeEventListener("keydown", takeInputDown, true);
		window.removeEventListener("keyup", takeInputUp, true);
		window.removeEventListener("resize", resizeCanvas, false);
		cancelAnimationFrame(animation_id);
		renderer = null;
		scene = null;
		camera = null;
		font = null;
		if (socket) {
			socket.close();
			socket = null;
		}
	},
	update(data) {
		if (game_status != PLAYING)
			return ;
		if (data.type == "tick") {
			game_data.ball_pos = data.b;
			game_data.racket_pos = data.r;
			updatePositions();
			return ;
		}
		if (data.type == "goal") {
			game_data.score = data.score;
			updateScore();
			return ;
		}
		if (data.type == "start") {
			game_data.ball_size = data.ball_size;
			game_data.racket_size = data.racket_size;
			game_data.score = data.score;
			updateSizes();
			updatePositions();
			updateScore();
			return ;
		}
		if (data.type == "win") {
			gameOver(data.player);
			return ;
		}
	},
	giveUp(socket) {
		bytes_array[0] = true;
		socket.send(bytes_array);
	}
};
