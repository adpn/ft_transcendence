import uuid
import json
import os

from django.http import JsonResponse, HttpRequest
from django.db.utils import IntegrityError

from .models import (
	GameRoom, 
	PlayerRoom, 
	Player, 
	Game, 
	Tournament, 
	TournamentRound,
	Participant,
	GameResult
)

from common import auth_client as auth

MAX_TOURNAMENT_ROOMS = 4
MAX_TOURNAMENT_PARTICIPANTS = 8

# creates a game and perform matchmaking...
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

def	find_tournament(request: HttpRequest) -> JsonResponse:
	# add pong game in database
	PONG = Game(game_name='pong', min_players=2)
	try:
		PONG.save()
	except IntegrityError:
		pass
	# todo: put game request handling in a function.
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

	# the player is a participant and is not eliminated, try to join the game room again.
	# this happens in case of disconnections or when moving to the next round.
	participant = Participant.objects.filter(player=player).first()
	if participant:
		if participant.status == "PLAYING":
			game_rooms_in_tournament = TournamentRound.objects.filter(
				tournament=tournament)
			# todo: if the room does not exist for some reason send an internal server error.
			player_room = PlayerRoom.objects.filter(
				player=player, 
				game_room__in=game_rooms_in_tournament).first()
			return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': player_room.game_room.room_name,
			'status': 'joined',
			'player_id': player_room.player.player_name
		}, status=200)

	# if the player is not a participant, try to join the oldest tournament that isn't full.
	tournament = Tournament.objects.filter(
		game__game_name=game.game_name,
		participants__lt=MAX_TOURNAMENT_PARTICIPANTS
	).order_by('created_at').first() # todo: need to setup a maximum amount of players.

	# if there is no tournament, create a new one.
	if not tournament:
		tournament = Tournament(game=game, tournament_id=str(uuid.uuid4()))
		game_room = GameRoom(room_name=str(uuid.uuid4()), game=game)
		player_room = PlayerRoom(
			player=player, 
			game_room=game_room,
			player_position=game_room.num_players
		)
		tround = TournamentRound(tournament=tournament, game_room=game_room)
		tournament.game_room_count += 1
		tournament.participants += 1
		game_room.num_players += 1
		game_room.save()
		player_room.save()
		tournament.save()
		tround.save()
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': game_room.room_name,
			'status': 'created',
			'player_id': player.player_name
		}, status=201)

	# try to find the room the player belongs to.
	game_rooms_in_tournament = TournamentRound.objects.filter(
		tournament=tournament)
	player_room = PlayerRoom.objects.filter(
		player=player, 
		game_room__in=game_rooms_in_tournament).first()

	# if player is already in a room return it. also means he is already a participant
	if player_room:
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': player_room.game_room.room_name,
			'status': 'playing',
			'player_id': player_room.player.player_name
		}, status=200)

	# get the oldest game_room in the tournament that isn't full
	game_room = game_rooms_in_tournament.filter(num_players__lt=game.min_players).order_by('create_at').first()
	if not game_room:
		# create new room, add the player to it add the game room to the tournament.
		game_room = GameRoom(room_name=str(uuid.uuid4()), game=game)
		player_room = PlayerRoom(
			player=player, 
			game_room=game_room,
			player_position=game_room.num_players
		)
		tround = TournamentRound(tournament=tournament, game_room=game_room)
		tournament.participants += 1
		game_room.num_players += 1
		game_room.save()
		player_room.save()
		tournament.save()
		tround.save()
		return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': game_room.room_name,
			'status': 'created',
			'player_id': player.player_name
		}, status=201)

	# if a game room was found add the player to it.
	participant = Participant(
		player=player, 
		tournament=tournament, 
		status="PLAYING")
	player_room = PlayerRoom(
		player=player, 
		game_room=game_room,
		player_position=game_room.num_players
	)
	tround = TournamentRound(tournament=tournament, game_room=game_room)
	game_room.num_players += 1
	tournament.participants += 1
	game_room.save()
	player_room.save()
	participant.save()
	tournament.save()
	tround.save()
	return JsonResponse({
			'ip_address': os.environ.get('IP_ADDRESS'),
			'game_room_id': game_room.room_name,
			'status': 'joined',
			'player_id': player.player_name
		}, status=200)

def game_stats_view(request : HttpRequest, user_id : int) -> JsonResponse:
    if request.method != 'GET':
        return JsonResponse({'status': 0, 'message': 'Only GET method is allowed'}, status=405)
    player = Player.objects.get(user_id=user_id)
    if not player:
        return JsonResponse({'status': 0, 'message': 'Player not found'}, status=404)
    games_won = GameResult.objects.filter(winner=player)
    games_lost = GameResult.objects.filter(loser=player)

    win_count = games_won.count()
    loss_count = games_lost.count()
    if win_count + loss_count == 0:
        return JsonResponse({'status': 1, 'total_games': 0}, status=200)

    games_data = []
    for game in games_won.union(games_lost):
        games_data.append({
            'is_winner': game.winner == player,
            'opponent': game.loser.user.username if game.winner == player else game.winner.user.username,
            'personal_score': game.winner_score if game.winner == player else game.loser_score,
            'opponent_score': game.loser_score if game.winner == player else game.winner_score,
            'game_date': game.game_date,
            'game_duration': game.game_duration,
        })

    response_data = {
        'status': 1,
        'total_games': win_count + loss_count,
        'total_wins': win_count,
        'win_percentage': round(win_count / (win_count + loss_count) * 100, 1),
        'games': games_data
    }

    return JsonResponse(response_data, status=200)
