from django.db import models

# Create your models here.

class Game(models.Model):
	game_name = models.CharField(max_length=50, unique=True)
	min_players = models.IntegerField(default=2)

class Player(models.Model):
	player_name = models.CharField(max_length=50, unique=True)
	player_id = models.IntegerField(primary_key=True)

class GameRoom(models.Model):
	room_name = models.CharField(max_length=100)
	# a game room can only have one game.
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	player_count = models.IntegerField(default=0)

# associate a player to a room.
class RoomPlayer(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	# a player can only have one room.
	game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
