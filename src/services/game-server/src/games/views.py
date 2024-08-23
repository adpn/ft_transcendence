import uuid
import json

from django.http import JsonResponse
from django.db.utils import IntegrityError

from .models import GameRoom, RoomPlayer, Player, Game
from http import client

def create_game(request):
	# add pong game in database
	PONG = Game(game_name='pong', min_players=2)
	try:
		PONG.save()
	except IntegrityError:
		pass

	conn = client.HTTPConnection('users:8000')
	conn.request('GET', '/get_user/', request.body, request.headers)
	response = conn.getresponse()
	if response.status != 200:
		return JsonResponse({
			'status': 0, 
			'message': 'Invalid token'}, status=401)
	user_data = json.loads(response.read().decode())
	try:
		game_request = json.loads(request.body)
		if 'game' not in game_request:
			return JsonResponse({
			'status': 0, 
			'message': "missing required field: {}".format('game')}, status=500)
	except json.decoder.JSONDecodeError:
		return JsonResponse({
			'status': 0, 
			'message': 'Couldn\'t read input'}, status=500)

	game = Game.objects.filter(game_name=game_request['game']).first()
	if not game:
		return JsonResponse({
			'status': 0, 
			'message': f"Game {game_request['game']} does not exist"}, status=404)

	room_player = RoomPlayer.objects.filter(player__player_name=user_data['username']).first()

	# the player is already into a game room so do nothing.
	if room_player:
		return JsonResponse({
				'game_room_id': room_player.game_room.room_name,
				'status': 'playing',
				'player_id': room_player.player.player_name
				}, status=200)

	# try to create a new player
	player = Player(player_name=user_data['username'], player_id=int(user_data['user_id']))
	try:
		player.save()
	except IntegrityError:
		pass

	# if the player is not found in any room, either assign it the oldest room that isn't full
	room = GameRoom.objects.filter(
		game__game_name=game_request['game'].lower(), 
		player_count__lt=game.min_players).order_by('created_at').first()

	if room:
		room.player_count += 1
		room.save()
		RoomPlayer(player=player, game_room=room).save()
		return JsonResponse({
				'game_room_id': room.room_name,
				'status': 'joined',
				'player_id': player.player_name
				}, status=200)

	# create new room if room does not exist
	room = GameRoom(room_name=str(uuid.uuid4()), game=game)
	room.player_count += 1
	room.save()
	RoomPlayer(player=player, game_room=room).save()
	return JsonResponse({
		'game_room_id': room.room_name,
		'status': 'created',
		'player_id': player.player_name
	}, status=200)
