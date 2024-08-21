from django.contrib import admin
from django.urls import include, path

from common import clients
from . import views

auth_client = clients.ServiceClient('user-management:8000')
# protected = views.NeedsAuthentication(views.ProtectedService())

urlpatterns = [
	# routes to the authentication microservice.
	path('login/', views.login_view(auth_client), name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('signup/', views.signup_view(auth_client), name='signup'),
	path('auth42/', views.auth42_view, name='auth42'),
	# path('protected/', protected, name='protected')
]