from django.contrib import admin
from django.urls import include, path

from . import views

# microservices.
auth_client = views.ServiceClient("authentication:8000")
# pong_client = views.ServiceClient("pong:8000")

#todo: for each path, call the view code
urlpatterns = [
	path('', views.index, name="index"),
	path('items/', views.ItemListView.as_view(), name='item-list'),
	# routes to the authentication microservice.
	path('login/', auth_client, name='login'),
	path('logout/', auth_client, name='logout'),
	path('signup/',  auth_client, name='signup'),
	path('auth/', auth_client, name="auth")
]
