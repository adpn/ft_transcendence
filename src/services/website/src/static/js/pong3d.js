import * as THREE from 'three';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';

const UP = true;
const DOWN = false;
const START = true;
const STOP = false;
const LEFT = false;
const RIGHT = true;

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
		score: [-1, -1]
	};
}
var renderer;
var animation_id;
var camera;
var font;
var is_focus = false;
var is_playing = false;
var bytes_array = new Uint8Array(4);

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
	light = light.clone();
	light.position.x *= -1;
	scene.add(light);
	object_ids.light[0] = light.id;
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

function makeXCord(number) {
	return number - 500;
}
function makeYCord(number) {
	return makeYHeight((number - 500) * -1);
}
function makeYHeight(number) {
	return number * HEIGHT / 1000;
}

function submitInput(dir, action, side) {
	bytes_array[0] = false;
	bytes_array[1] = dir;
	bytes_array[2] = action;
	bytes_array[3] = side;
	socket.send(bytes_array);
}

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

export var Pong3d = {
	name: "pong",
	canvas_context: "3D",
	load(canv) {
		canvas = canv;
		canvas.setAttribute("tabindex", "-1");
		canvas.addEventListener("focus", () => { is_focus = true; });
		canvas.addEventListener("blur", () => { is_focus = false; });
		if (loadThreejs() == -1) {
			return ;
		}
		is_playing = true;
		window.addEventListener("resize", resizeCanvas, false);
		canvas.focus();
	},
	start(sockt) {
		socket = sockt;
		is_playing = true;
		canvas.focus();
		window.addEventListener("keydown", takeInputDown, true);
		window.addEventListener("keyup", takeInputUp, true);
	},
	clear() {
		is_playing = false;
		window.removeEventListener("keydown", takeInputDown, true);
		window.removeEventListener("keyup", takeInputUp, true);
		window.removeEventListener("resize", resizeCanvas, false);
		cancelAnimationFrame(animation_id);
		renderer = null;
		scene = null;
		camera = null;
		font = null;
	},
	update(data) {
		if (is_playing != true)
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
	}
};
