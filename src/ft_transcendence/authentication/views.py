from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

# Create your views here.

def login_view(request):
	#todo: check if the fields are present
	data = json.loads(request.body)
	username = data["username"]
	password = data["password"]
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		#todo: need a login response json -> should contain images
		return JsonResponse({}, status=200)
	else:
		return JsonResponse({}, status=404)

def logout_view(request):
	logout(request)
	return JsonResponse({}, status=200)

def signup_view(request):
	data = json.loads(request.body)
	user = User.objects.create_user(data["username"])
	#todo: check if the fields are present
	#todo: perform hashing and salting before storing the password.
	user.password = data["password"]
	# todo: catch duplicate error for saving and return the appropriate error.
	user.save()
	#todo: check if username is already taken...
	return JsonResponse({}, status=200)
