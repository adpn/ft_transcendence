import uuid

from django.http import JsonResponse

from importlib import import_module

from django.conf import settings

# temporary implementation of matchmaking

engine = import_module(settings.SESSION_ENGINE)

GAME_ROOMS = []

class GameRoom:
	def __init__(self, room_name) -> None:
		self._num_players = 0
		self._room_name = room_name
		self._players = {}

	@property
	def num_players(self):
		return self._num_players

	@property
	def room_id(self):
		return self._room_name

	def add_player(self, player_id):
		self._num_players += 1
		self._players[player_id] = player_id
		return self._room_name

	def __contains__(self, value):
		return value in self._players

from http import client

def create_game(request):
	#todo: the request body should contain the game name, then fetch game settings from the game-server.
	# if not request.user.is_authenticated:
	# 	return JsonResponse({}, status=401)
	conn = client.HTTPConnection('users:8000')
	conn.request('GET', '/check_token/', request.body, request.headers)
	response = conn.getresponse()
	if response.status != 200:
		return JsonResponse({}, status=401)
	session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

	# check if is already playing
	for game_room in GAME_ROOMS:
		# todo: conditions for a room to be ready depend on game settings.
		if game_room.num_players == 2 and session_key in game_room:
			return JsonResponse({
				'game_room_id': game_room.room_id,
				'status': 'playing',
				'player_id': session_key
				}, status=200)

	# find a game room
	for game_room in GAME_ROOMS:
		# todo: conditions for a room to be ready depend on game settings.
		if game_room.num_players == 1 and session_key not in game_room:
			# remove the game room
			# GAME_ROOMS.remove(game_room)
			return JsonResponse({
				'game_room_id': game_room.add_player(session_key),
				'status': 'joined',
				'player_id': session_key
				}, status=200)

	# create a new game room
	room_id = str(uuid.uuid4())
	# add it to the session store.
	game_room = GameRoom(room_id)
	GAME_ROOMS.append(game_room)
	# save the session key.
	#session_store.save(True)
	return JsonResponse({
		'game_room_id': game_room.add_player(session_key),
		'status': 'new-room',
		'player_id': session_key}, status=201)
