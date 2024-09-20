import uuid
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpRequest
from django.db.utils import IntegrityError
import datetime

from .models import (
	GameRoom, 
	PlayerRoom, 
	Player, 
	Game, 
	Tournament, 
	TournamentGameRoom,
	TournamentParticipant,
	GameResult
)

from common import auth_client as auth

MAX_TOURNAMENT_PARTICIPANTS = 8
# creates a game and performs matchmaking...
# TODO: handle local games
def create_game(request):
	# add pong game in database
	PONG = Game(game_name='pong', min_players=2)
	try:
		PONG.save()
	except IntegrityError:
		pass

	user_data = auth.get_user(request)
	if not user_data:
		return JsonResponse({
			'status': 0, 
			'message': 'Invalid token'
		}, status=401)
	# TODO: check if the game is a local game.
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

	room_player = PlayerRoom.objects.filter(player__player_id=int(user_data['user_id'])).first()

	# the player is already into a game room so do nothing.
	if room_player:
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': room_player.game_room.room_name,
			'status': 'playing',
			'player_id': room_player.player.player_name
			}, status=200)

	# try to create a new player
	player = Player(
		player_name=user_data['username'], 
		player_id=int(user_data['user_id']))
	try:
		player.save()
	except IntegrityError:
		pass

	# if the player is not found in any room, either assign it the oldest room that isn't full
	# or create a new room
	rooms = GameRoom.objects.filter(
		game__game_name=game_request['game'].lower(),
		num_players__lt=game.min_players).order_by('created_at')

	room = rooms.first()
	if room:
		room.num_players += 1
		room.save(update_fields=['num_players'])
		PlayerRoom(
			player=player, 
			game_room=room, 
			player_position=room.num_players - 1).save()
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': room.room_name,
			'status': 'joined',
			'player_id': player.player_name
			}, status=200)

	# create new room if room does not exist
	room = GameRoom(
		room_name=str(uuid.uuid4()), 
		game=game)
	room.num_players += 1
	room.save()
	PlayerRoom(
		player=player,
		game_room=room, 
		player_position=room.num_players - 1).save()
	return JsonResponse({
		'ip_address': os.environ.get('IP_ADDRESS'),
		'game_room_id': room.room_name,
		'status': 'created',
		'player_id': player.player_name
	}, status=201)

def add_player_to_room(player: Player, game_room: GameRoom) -> PlayerRoom:
	player_room = PlayerRoom(
		player=player, 
		game_room=game_room,
		player_position=game_room.num_players)

	game_room.num_players += 1
	game_room.save(update_fields=['num_players'])
	player_room.save()
	return player_room

def create_game_room(player: Player, game: Game) -> GameRoom:
	# create new room, add the player to it
	game_room = GameRoom(room_name=str(uuid.uuid4()), game=game)
	game_room.save()
	# map player to game room.
	add_player_to_room(player, game_room)
	return game_room

def add_participant(
	player: Player, 
	tournament: Tournament, 
	is_host=False) -> TournamentParticipant:

	participant = TournamentParticipant(
		player=player, 
		tournament=tournament, 
		status="PLAYING",
		is_host=is_host)

	participant.tournament_position = tournament.participants
	tournament.participants += 1
	tournament.save()
	participant.save()
	return participant

# TODO: api call for adding a guest to the database
def add_guests(request: HttpRequest) -> JsonResponse:
	pass

def join_tournament(
	game: Game,
	player:Player,
	tournament: Tournament,
	participant: TournamentParticipant = None):

	# join the tournament by either reconnecting, joining a room or create a nes room.
	if not participant:
		game_rooms_in_tournament = TournamentGameRoom.objects.filter(
			tournament=tournament
			).values_list('game_room', flat=True)
	else:
		# the tournament room that matches the round of the participant.
		game_rooms_in_tournament = TournamentGameRoom.objects.filter(
			tournament=tournament,
			tournament_round=participant.tournament_round,
			).values_list('game_room', flat=True)

	player_room = PlayerRoom.objects.filter(
		player=player, 
		game_room__in=game_rooms_in_tournament).first()

	# if player is already in a room return it (reconnecting him to the room)
	if player_room:
		print("RECONNECTION", player_room, flush=True)
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': player_room.game_room.room_name,
			'status': 'playing',
			'player_id': player_room.player.player_name
		}, status=200)

	if not participant:
		add_participant(player, tournament)

	# get the oldest game_room in the tournament that isn't full 
	# TODO: (Maybe select the game room at a certain position given the participant position ?)
	game_room = GameRoom.objects.filter(
		room_name__in=game_rooms_in_tournament,
		num_players__lt=game.min_players
		).order_by('created_at').first()

	if not game_room:
		game_room = create_game_room(player, game)
		print("NEW GAME ROOM", game_room.room_name, flush=True)
		if tournament:
			# map game room to tournament.
			tgame_room = TournamentGameRoom(tournament=tournament, game_room=game_room)
			tgame_room.save()
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': game_room.room_name,
			'status': 'created',
			'player_id': player.player_name
		}, status=201)
	add_player_to_room(player, game_room)
	return JsonResponse({
		'ip_address': os.environ.get('IP_ADDRESS'),
		'game_room_id': game_room.room_name,
		'status': 'joined',
		'player_id': player.player_name}, status=200)

def create_tournament(player: Player, game:Game, max_participants=8) -> GameRoom:
	tournament = Tournament(
		game=game, 
		tournament_id=str(uuid.uuid4()), 
		max_participants=max_participants)
	game_room = create_game_room(player, game)
	add_participant(player, tournament, True)
	# map game room to tournament
	tgame_room = TournamentGameRoom(
		tournament=tournament,
		game_room=game_room)
	tgame_room.save()
	return game_room

def create_or_join_tournament(player: Player, game:Game, max_participants=8) -> JsonResponse:
	print("NEW PARTICIPANT", flush=True)
	# if the player is not a participant, 
	# try to join the oldest tournament that isn't full.
	tournament = Tournament.objects.filter(
		game__game_name=game.game_name,
		participants__lt=MAX_TOURNAMENT_PARTICIPANTS).order_by('created_at').first()

	# if there is no tournament, create a new one and a new game room.
	if not tournament:
		game_room = create_tournament(player, game)
		print("NEW TOURNAMENT", game_room, flush=True)
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': game_room.room_name,
			'status': 'created',
			'player_id': player.player_name
			}, status=201)
	print("NEW PARTICIPANT JOIN", flush=True)
	return join_tournament(game, player, tournament)

def	find_tournament(request: HttpRequest) -> JsonResponse:
	# add pong game in database
	PONG = Game(game_name='pong', min_players=2)
	try:
		PONG.save()
	except IntegrityError:
		pass
	# todo: put game request handling in a function.
	# TODO: check if it local.
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

	user_data = auth.get_user(request)
	if not user_data:
		return JsonResponse({
			'status': 0, 
			'message': 'Invalid token'
		}, status=401)

	''' TODO:
		----
		if the game is in local mode, get the PARTICIPANT in the json file, check if it is a guest or the host then proceed as usual ?
		this would mean that we make two calls for finding a tournament for each participant. the client is responsible for making the proper
		request, but the server knows who's eliminated.
	'''

	# try to create a new player
	player = Player(
		player_name=user_data['username'], 
		player_id=int(user_data['user_id']))
	try:
		player.save()
	except IntegrityError:
		pass

	game = Game.objects.filter(game_name=game_request['game']).first()
	if not game:
		return JsonResponse({
			'status': 0,
			'message': f"Game {game_request['game']} does not exist"}, status=404)

	participant = TournamentParticipant.objects.filter(player=player).first()
	# ================== RECONNECT OR MOVE TO THE NEXT ROUND ========================
	if participant:
		'''
		TODO: if the participant is eliminated, create or join another tournament.
		'''
		if participant.status == "ELIMINATED" or participant.status == "WINNER":
			return create_or_join_tournament(player, game)
		elif participant.status == "PLAYING":
			# if the participant is not eliminated then 
			return join_tournament(game, player, participant.tournament, participant)
	return create_or_join_tournament(player, game)

@csrf_exempt
def game_stats(request: HttpRequest, user_id : int) -> JsonResponse:
	if request.method != 'GET':
		return JsonResponse({'status': 0, 'message': 'Only GET method is allowed'}, status=405)

	# the player never played a game
	if not Player.objects.filter(player_id=user_id).exists():
		return JsonResponse({'status': 0, 'message': 'Player never played'}, status=200)

	player = Player.objects.get(player_id=user_id)

	list_games = Game.objects.all()
	if list_games.count() == 0:
		return JsonResponse({'status': 0, 'message': 'No game found'}, status=500)

	response_data = {'status': 1}
	nb_games = 0
	for game in list_games:
		games_won = GameResult.objects.filter(winner=player, game=game)
		games_lost = GameResult.objects.filter(loser=player, game=game)

		win_count = games_won.count()
		loss_count = games_lost.count()
		if win_count + loss_count == 0:
			response_data[game.game_name] = {
				'total_games': 0
			}
			continue
		nb_games += 1
	
		games_data = []
		total_points = 0
		total_total_points = 0
		playtime = 0
		for result in games_won.union(games_lost):
			total_points += result.winner_score if result.winner == player else result.loser_score
			total_total_points += result.winner_score + result.loser_score
			playtime += result.game_duration
			games_data.append({
				'is_winner': result.winner == player,
				'opponent_id': result.loser.player_id if result.winner == player else result.winner.player_id,
				'personal_score': result.winner_score if result.winner == player else result.loser_score,
				'opponent_score': result.loser_score if result.winner == player else result.winner_score,
				'game_date': result.game_date,
				'game_duration': str(datetime.timedelta(seconds=result.game_duration))
			})

		playtime = str(datetime.timedelta(seconds=playtime))
		# maybe add average score, average duration
		response_data[game.game_name] = {
			'total_games': win_count + loss_count,
			'total_wins': win_count,
			'average_score': round(total_points / (win_count + loss_count), 1),
			'playtime' : playtime,
			'precision': round(total_points / total_total_points * 100, 1),
			'win_percentage': round(win_count / (win_count + loss_count) * 100, 1),
			'games': games_data
		}

	if nb_games == 0:
		return JsonResponse({'status': 0, 'message': 'Player never played'}, status=200)
	return JsonResponse(response_data, status=200)
