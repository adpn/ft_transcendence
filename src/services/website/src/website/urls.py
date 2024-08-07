from django.contrib import admin
from django.urls import include, path

from . import views
from .views import ItemListView, SignUpView, LoginView, LogoutView
# add other microservice clients here...
# import clients

# auth_client = clients.AuthenticationClient("authentication:8000")

#todo: for each path, call the view code
urlpatterns = [
	path('', views.index, name="index"),
	path('items/', ItemListView.as_view(), name='item-list'),
	# routes to the authentication microservice.
	# path('auth/login/', views.ViewFactory(views.LoginView, auth_client=auth_client), name='login'),
	# path('auth/logout/', views.ViewFactory(views.LogoutView, auth_client=auth_client), name='logout'),
	# path('auth/signup/',  views.ViewFactory(views.SignUpView, auth_client=auth_client), name='signup')
]
