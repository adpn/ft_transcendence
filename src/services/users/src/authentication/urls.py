from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
	# path('authenticate/', views.authenticate),
	path('signup/', views.sign_up_view),
	path('get_user/', views.get_user_view),
	path('login/', views.login_view),
	path('logout/', views.logout_view),
	path('is_authenticated/', views.is_authenticated_view),
	path('auth42/', views.auth42_view),
	path('check_token/', views.check_token)
]
