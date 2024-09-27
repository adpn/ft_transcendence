from django.db import models

# Create your models here.
class UserChannel(models.Model):
	user_id = models.IntegerField(primary_key=True)
	channel_name = models.CharField(max_length=100, null=False)