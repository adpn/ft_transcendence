from django.contrib import admin
from django.urls import include, path


from . import views

urlpatterns = [
	# routes to the authentication microservice.
	path('create_game/', views.create_game, name='create_game'),
	path('join_tournament/', views.find_tournament, name='join_tournament')
]