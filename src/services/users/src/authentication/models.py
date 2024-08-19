from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    username42 = models.CharField(max_length=25, default=None, null=True)
    username = models.CharField(max_length=25, unique=True)
