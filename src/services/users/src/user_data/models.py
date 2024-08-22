from django.db import models

class UserProfile(models.Model):
    user_id = models.IntegerField()
    profile_picture = models.FileField(upload_to='profile_pictures/', default='profile_pictures/default.jpg')

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    winner_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='games_won')
    loser_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='games_lost')
    score_user1 = models.IntegerField()
    score_user2 = models.IntegerField()
    game_date = models.DateTimeField()
    game_duration = models.DurationField()
