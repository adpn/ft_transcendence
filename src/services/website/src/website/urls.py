from django.contrib import admin
from django.urls import include, path

from . import views

# pong_client = views.ServiceClient("pong:8000")

#todo: for each path, call the view code
urlpatterns = [
	path('', views.index, name="index")
	# path('is_authenticated/', views.is_authenticated, name='login')
	# routes to the authentication microservice.
	# path('login/', auth_client, name='login'),
	# path('logout/', auth_client, name='logout'),
]
