from django.db import models
from user_data.models import UserProfile

class Relation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_relations')
    friend = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='friend_relations')
    status = models.BooleanField(default=False)