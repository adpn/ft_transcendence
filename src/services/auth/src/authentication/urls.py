from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('signup/', views.signup_view, name='signup'),
	#path('auth/', views.auth42_view, name='auth42')
]
