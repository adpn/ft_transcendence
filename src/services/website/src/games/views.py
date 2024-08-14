import uuid

from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
games_rooms = []

def create_game(request):
	player_id = request.session.get('player_id')
	
	# create new player
	if not player_id:
		player_id = str(uuid.uuid4())
		request.session['player-id'] = player_id

	# find a game room
	for game_room in games_rooms:
		player_id = request.session['player_id']
		if game_room.num_players == 1 and player_id not in game_room:
			# remove the game room
			games_rooms.remove(game_room)
			return JsonResponse({
				'game-room-id': game_room.add_player(player_id),
				'status': 'ready'}, status=200)
