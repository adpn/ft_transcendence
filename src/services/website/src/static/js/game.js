/*
	- fetch /game/create
	- receive json
	- connect with gameid ??
*/

// is 'session' send in this request automatically ??
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
		const socket = new WebSocket("ws://pong/" + data[room-id]); // ws for now to do testing, wss later.		also there is no way this is the correct url
	});
}
