from django.db import models
from authentication.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.FileField(upload_to='profile_pictures/', default='profile_pictures/default.jpg')
    online_status = models.BooleanField(default=False)

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    winner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='games_won')
    loser = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='games_lost')
    score_winner = models.IntegerField()
    score_loser = models.IntegerField()
    game_date = models.DateTimeField()
    game_duration = models.DurationField()
