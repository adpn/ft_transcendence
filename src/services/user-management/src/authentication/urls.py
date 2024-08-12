from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

from . import views

def protected(request):
	if request.user.is_authenticated:
		return JsonResponse({'message': "Hello!"}, status=200)
	return JsonResponse({'message': "Hello!"}, status=401)

urlpatterns = [
	path('signup/', views.signup_view, name='signup'),
	#path('delete-account/', views.delete_account_view, name='delete-account'),
	path('authenticate/', views.authenticate_view, name='authenticate')
]
