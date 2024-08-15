from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_42 = models.BooleanField(default=False)
    username = models.CharField(max_length=25)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['username']
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'is_42'],
                name='unique_username_with_is_42'
            )
        ]
    # profile_picture = models.FileField(upload_to=None, height_field=512, width_field=512, max_length=512)