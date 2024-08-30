from django.db import models

# Create your models here.

class Game(models.Model):
	game_name = models.CharField(max_length=50, unique=True)
	min_players = models.IntegerField(default=2)

class Tournament(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	tournament_id = models.CharField(max_length=100, primary_key=True)
	game_room_count = models.IntegerField(default=0)
	participants = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	closed = models.BooleanField(default=True)

class Player(models.Model):
	player_name = models.CharField(max_length=50, unique=True)
	player_id = models.IntegerField(primary_key=True)

class Participant(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	status = models.CharField(max_length=20, default="PLAYING")

class GameRoom(models.Model):
	room_name = models.CharField(max_length=100, primary_key=True)
	# a game room can only have one game.
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	num_players = models.IntegerField(default=0)
	in_session = models.BooleanField(default=False)

class TournamentRound(models.Model):
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
	round_number = models.IntegerField(default=0)

# associate a player to a room.
class PlayerRoom(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	# a player can only have one room.
	game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
	player_position = models.IntegerField(default=0)

class GameResult(models.Model):
	winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='won_games')
	loser = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='lost_games')
	winner_score = models.IntegerField(default=0)
	loser_score = models.IntegerField(default=0)
	game_duration = models.IntegerField(default=0)
	game_date = models.DateTimeField(auto_now_add=True)
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
