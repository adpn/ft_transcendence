# games = clients.ServiceClient('game-server:8000')
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
	# routes to the authentication microservice.
	path('create_game/', views.create_game, name='create_game'),
	# path('protected/', protected, name='protected')
]